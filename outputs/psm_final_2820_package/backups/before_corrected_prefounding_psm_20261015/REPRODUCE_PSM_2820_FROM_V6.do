version 19
clear all
set more off

global PSM_ROOT "C:/Users/user/Documents/VD/outputs/psm_final_2820_package"
global PREMATCH "C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms/exact matched sample v6 unmatched.xlsx"
global DIAG "$PSM_ROOT/replicated_appendix"
global APPUNION "C:/Users/user/Documents/VD/outputs/csdid_union_corrected_3yr/application_level_union_corrected_visible_mismatches.csv"
global FIRMMAP "C:/Users/user/Documents/VD/outputs/csdid_ultimately_granted_primary/csdid_ultimately_granted_full7316_controls.dta"
capture mkdir "$DIAG"

capture log close
log using "$PSM_ROOT/REPRODUCE_PSM_2820_FROM_V6.log", text replace

********************************************************************************
* 1. PRE-MATCH FIRM-LEVEL SAMPLE: 7,316 FIRMS
********************************************************************************
import excel using "$PREMATCH", firstrow clear

* Stata may import the headers with slightly different legal names.
capture confirm variable OrganizationName
if _rc rename OrganizationNameURL organization_url
capture confirm variable OrganizationName

capture confirm numeric variable VD_Backing
if _rc destring VD_Backing, replace

* Historical treatment definition used for the archived 2,820 sample.
replace VD_Backing = 1 if inlist(OrganizationName,"Dermira","Eargo")
replace VD_Backing = 0 if inlist(OrganizationName,"Cortex","Nomi1")

* The funding amount is missing for 30 of the 1,440 VD-backed firms.
* Those 30 cannot enter a logit containing Log(Total Funding Amount_VD),
* leaving 1,410 eligible treated firms.
capture drop ln_Total_Funding_Amount_FirstVD
gen double ln_Total_Funding_Amount_FirstVD = ln(Total_Funding_Amount_FirstVD + 1)

capture confirm numeric variable Founding_Year
if _rc destring Founding_Year, replace
* All controls use the hypothetical reference year Founding Year + 5.
replace VDYear = Founding_Year + 5 if VD_Backing==0
capture confirm numeric variable TimeToFirst_VC
if _rc destring TimeToFirst_VC, replace
capture confirm numeric variable Grant_VD
if _rc destring Grant_VD, replace
capture confirm numeric variable NumberOfFunding_Rounds_FirstVD
if _rc destring NumberOfFunding_Rounds_FirstVD, replace

capture confirm numeric variable Region2
if _rc {
    encode Region2, gen(Region2_n)
    drop Region2
    rename Region2_n Region2
}
capture confirm numeric variable Industry2
if _rc {
    encode Industry2, gen(Industry2_n)
    drop Industry2
    rename Industry2_n Industry2
}

count
assert r(N)==7316
count if VD_Backing==1
assert r(N)==1440
count if VD_Backing==0
assert r(N)==5876

********************************************************************************
* 2. BUILD PRE-REFERENCE AND WINDOW-3 APPLICATION COUNTS BEFORE MATCHING
********************************************************************************
tempfile firm_reference application_counts
preserve
    gen str244 name_key=ustrlower(OrganizationName)
    replace name_key=ustrregexra(name_key,"[^a-z0-9]","")
    gen double reference_year=VDYear
    keep name_key reference_year
    bysort name_key: egen reference_min=min(reference_year)
    bysort name_key: egen reference_max=max(reference_year)
    assert reference_min==reference_max
    bysort name_key: keep if _n==1
    drop reference_min reference_max
    save `firm_reference', replace

    import delimited using "$APPUNION", clear varnames(1) encoding(utf8)
    keep if inrange(filing_year,2010,2024)
    duplicates drop full_firm_id application_id, force
    count
    assert r(N)==39249
    gen str244 name_key=ustrlower(organization_name)
    replace name_key=ustrregexra(name_key,"[^a-z0-9]","")
    merge m:1 name_key using `firm_reference', keep(match) nogen
    gen byte app_at_vd=(filing_year<=reference_year)
    gen byte app_win3=inrange(filing_year-reference_year,0,3)
    collapse (sum) patent_application_VD=app_at_vd ///
                   patent_application_win3=app_win3, by(name_key)
    save `application_counts', replace
restore

capture drop patent_application_VD patent_application_win3 name_key
gen str244 name_key=ustrlower(OrganizationName)
replace name_key=ustrregexra(name_key,"[^a-z0-9]","")
merge m:1 name_key using `application_counts', keep(master match) gen(_merge_appcounts)
replace patent_application_VD=0 if missing(patent_application_VD)
replace patent_application_win3=0 if missing(patent_application_win3)
label var patent_application_VD "Applications filed through actual or hypothetical VD year"
label var patent_application_win3 "Applications filed in years t=0 to t+3"

assert patent_application_VD==9 if OrganizationName=="Affirmed Networks"
assert patent_application_VD==38 & patent_application_win3==16 if OrganizationName=="AliveCor"
assert patent_application_VD==9 & patent_application_win3==0 if OrganizationName=="Health Outcomes Sciences"

********************************************************************************
* 3. 1:1 NEAREST-NEIGHBOR PSM, COMMON SUPPORT, WITHOUT REPLACEMENT
*
* Matching variables stated in the manuscript:
* - Log(Total Funding Amount_VD)
* - Number of Funding Rounds_VD
* - Patent applications filed through the reference year
* - Founding Year
* - Region
* - Industry
* - Time to First VC
********************************************************************************
capture which psmatch2
if _rc ssc install psmatch2

set seed 20250901
psmatch2 VD_Backing ///
    i.Founding_Year ///
    i.Region2 ///
    i.Industry2 ///
    ln_Total_Funding_Amount_FirstVD ///
    NumberOfFunding_Rounds_FirstVD ///
    patent_application_VD ///
    TimeToFirst_VC, ///
    logit neighbor(1) noreplacement common

gen byte matched_2820 = (_weight==1) if !missing(_weight)
replace matched_2820 = 0 if missing(matched_2820)

tab VD_Backing matched_2820, missing
count if matched_2820==1
display as result "Matched observations = " r(N)
count if matched_2820==1 & VD_Backing==1
display as result "Matched VD-backed firms = " r(N)
count if matched_2820==1 & VD_Backing==0
display as result "Matched controls = " r(N)

count if matched_2820==1
assert r(N)==2820
count if matched_2820==1 & VD_Backing==1
assert r(N)==1410
count if matched_2820==1 & VD_Backing==0
assert r(N)==1410

********************************************************************************
* 4. SAVE MATCHED SAMPLE AND APPLICATION-COUNT AUDIT
********************************************************************************
* Firm-level audit against the legacy granted-patent variable.  Grant_3years
* and patent_application_win3 measure different events, so disagreement is
* expected; this file is intended to make implausible firm mappings visible.
preserve
    keep no OrganizationName VD_Backing Founding_Year VDYear Grant_VD ///
         Grant_3years patent_application_VD patent_application_win3 ///
         _merge_appcounts
    sort OrganizationName
    export delimited using "$DIAG/patent_application_count_audit.csv", replace
restore

drop _merge_appcounts

save "$PSM_ROOT/psm_stata_full7316_with_scores.dta", replace
preserve
    keep if matched_2820==1
    save "$PSM_ROOT/psm_stata_matched_2820.dta", replace
    export delimited using "$PSM_ROOT/psm_stata_matched_2820.csv", replace
restore

********************************************************************************
* 4. LEGACY PSTEST OUTPUT
********************************************************************************
pstest ln_Total_Funding_Amount_FirstVD ///
    NumberOfFunding_Rounds_FirstVD patent_application_VD TimeToFirst_VC, both

********************************************************************************
* 5. TABLE A6: STANDARDIZED DIFFERENCES AND VARIANCE RATIOS
* Balance is assessed with SMDs, not primarily with t-tests.
* Variance ratios are reported for continuous covariates only.
********************************************************************************
gen byte psm_esample = !missing(_pscore)

tempname BAL
postfile `BAL' str64 covariate str20 variable_type ///
 double treated_before control_before smd_before variance_ratio_before ///
 treated_after control_after smd_after variance_ratio_after ///
 using "$DIAG/Table_A6_balance.dta", replace

local continuous ln_Total_Funding_Amount_FirstVD ///
 NumberOfFunding_Rounds_FirstVD patent_application_VD Founding_Year TimeToFirst_VC
foreach v of local continuous {
    local lab "`v'"
    if "`v'"=="ln_Total_Funding_Amount_FirstVD" local lab "Log total funding amount at reference year"
    if "`v'"=="NumberOfFunding_Rounds_FirstVD" local lab "Number of funding rounds at reference year"
    if "`v'"=="patent_application_VD" local lab "Patent applications through reference year"
    if "`v'"=="Founding_Year" local lab "Founding year"
    if "`v'"=="TimeToFirst_VC" local lab "Time to first VC"

    quietly summarize `v' if VD_Backing==1 & psm_esample
    local mt0=r(mean)
    local vt0=r(Var)
    quietly summarize `v' if VD_Backing==0 & psm_esample
    local mc0=r(mean)
    local vc0=r(Var)
    local pool0=sqrt((`vt0'+`vc0')/2)

    quietly summarize `v' if VD_Backing==1 & matched_2820
    local mt1=r(mean)
    local vt1=r(Var)
    quietly summarize `v' if VD_Backing==0 & matched_2820
    local mc1=r(mean)
    local vc1=r(Var)
    local pool1=sqrt((`vt1'+`vc1')/2)

    post `BAL' ("`lab'") ("Continuous") ///
      (`mt0') (`mc0') (cond(`pool0'>0,(`mt0'-`mc0')/`pool0',0)) (cond(`vc0'>0,`vt0'/`vc0',.)) ///
        (`mt1') (`mc1') (cond(`pool1'>0,(`mt1'-`mc1')/`pool1',0)) (cond(`vc1'>0,`vt1'/`vc1',.))
}

* Region2 and Industry2 are reported as the original variables, one row each,
* matching the historical Appendix table. Variance ratios are omitted because
* their numeric codes represent categories rather than continuous quantities.
foreach v in Region2 Industry2 {
    if "`v'"=="Region2" local lab "Region2"
    if "`v'"=="Industry2" local lab "Industry2"
    quietly summarize `v' if VD_Backing==1 & psm_esample
    local mt0=r(mean)
    local vt0=r(Var)
    quietly summarize `v' if VD_Backing==0 & psm_esample
    local mc0=r(mean)
    local vc0=r(Var)
    local pool0=sqrt((`vt0'+`vc0')/2)
    quietly summarize `v' if VD_Backing==1 & matched_2820
    local mt1=r(mean)
    local vt1=r(Var)
    quietly summarize `v' if VD_Backing==0 & matched_2820
    local mc1=r(mean)
    local vc1=r(Var)
    local pool1=sqrt((`vt1'+`vc1')/2)
    post `BAL' ("`lab'") ("Categorical code") ///
      (`mt0') (`mc0') (cond(`pool0'>0,(`mt0'-`mc0')/`pool0',0)) (.) ///
      (`mt1') (`mc1') (cond(`pool1'>0,(`mt1'-`mc1')/`pool1',0)) (.)
}
postclose `BAL'

preserve
use "$DIAG/Table_A6_balance.dta", clear
gen abs_smd_before=abs(smd_before)
gen abs_smd_after=abs(smd_after)
gen byte exceeds_010_after=abs_smd_after>.10 if !missing(abs_smd_after)
format treated_before control_before treated_after control_after %9.3f
format smd_before smd_after variance_ratio_before variance_ratio_after %9.3f
export delimited using "$DIAG/Table_A6_balance.csv", replace

quietly summarize abs_smd_before, meanonly
scalar max_smd_before=r(max)
quietly summarize abs_smd_after, meanonly
scalar max_smd_after=r(max)
count if exceeds_010_after==1
scalar rows_over_010=r(N)

********************************************************************************
* 5. LOVE PLOT
********************************************************************************
gsort -abs_smd_before
gen plot_order=_n
forvalues i=1/`=_N' {
    local lab=covariate[`i']
    label define balance_order `i' "`lab'", add
}
label values plot_order balance_order

twoway ///
 (scatter plot_order abs_smd_before, msymbol(O) mcolor(maroon)) ///
 (scatter plot_order abs_smd_after, msymbol(D) mcolor(navy)), ///
 xline(.10, lpattern(dash) lcolor(gs7)) ///
 ylabel(1(1)`=_N', valuelabel angle(horizontal) labsize(vsmall)) ///
 xtitle("Absolute standardized mean difference") ytitle("") ///
 title("Covariate balance before and after matching") ///
 legend(order(1 "Before matching" 2 "After matching") rows(1) position(6)) ///
 graphregion(color(white)) plotregion(color(white)) name(LOVE_A2, replace)
graph export "$DIAG/Figure_A2_Love_plot.png", replace width(3000)
graph save "$DIAG/Figure_A2_Love_plot.gph", replace
restore

********************************************************************************
* 6. FIGURE A1: PROPENSITY-SCORE OVERLAP BEFORE AND AFTER MATCHING
* Improved overlap is descriptive; identical densities are not required.
********************************************************************************
twoway ///
 (kdensity _pscore if VD_Backing==1 & psm_esample, lcolor(maroon) lwidth(medthick)) ///
 (kdensity _pscore if VD_Backing==0 & psm_esample, lcolor(navy) lpattern(dash) lwidth(medthick)), ///
 title("Panel A. Before matching") xtitle("Estimated propensity score") ytitle("Density") ///
 legend(order(1 "VD-backed" 2 "VC-only")) graphregion(color(white)) name(PS_PRE, replace)

twoway ///
 (kdensity _pscore if VD_Backing==1 & matched_2820, lcolor(maroon) lwidth(medthick)) ///
 (kdensity _pscore if VD_Backing==0 & matched_2820, lcolor(navy) lpattern(dash) lwidth(medthick)), ///
 title("Panel B. After 1:1 matching") xtitle("Estimated propensity score") ytitle("Density") ///
 legend(order(1 "VD-backed" 2 "Matched VC-only")) graphregion(color(white)) name(PS_POST, replace)

graph combine PS_PRE PS_POST, cols(2) ///
 title("Propensity-score distributions before and after matching") ///
 graphregion(color(white)) name(FIG_A1, replace)
graph export "$DIAG/Figure_A1_propensity_score_overlap.png", replace width(3600)
graph save "$DIAG/Figure_A1_propensity_score_overlap.gph", replace

********************************************************************************
* 7. COMMON-SUPPORT INFORMATION
********************************************************************************
quietly summarize _pscore if VD_Backing==1 & psm_esample, meanonly
scalar treated_min=r(min)
scalar treated_max=r(max)
quietly summarize _pscore if VD_Backing==0 & psm_esample, meanonly
scalar control_min=r(min)
scalar control_max=r(max)
scalar support_lower=max(treated_min,control_min)
scalar support_upper=min(treated_max,control_max)
gen byte empirical_support=inrange(_pscore,support_lower,support_upper) if psm_esample

tempname SUP
postfile `SUP' str60 statistic double value using "$DIAG/Table_A6_common_support.dta", replace
post `SUP' ("Treated propensity-score minimum") (treated_min)
post `SUP' ("Treated propensity-score maximum") (treated_max)
post `SUP' ("Control propensity-score minimum") (control_min)
post `SUP' ("Control propensity-score maximum") (control_max)
post `SUP' ("Empirical common-support lower bound") (support_lower)
post `SUP' ("Empirical common-support upper bound") (support_upper)
foreach g in 0 1 {
    quietly count if VD_Backing==`g' & psm_esample
    post `SUP' ("Group `g': propensity-score estimation N") (r(N))
    quietly count if VD_Backing==`g' & psm_esample & empirical_support==1
    post `SUP' ("Group `g': within empirical support N") (r(N))
    quietly count if VD_Backing==`g' & psm_esample & empirical_support==0
    post `SUP' ("Group `g': outside empirical support N") (r(N))
    quietly count if VD_Backing==`g' & matched_2820
    post `SUP' ("Group `g': final matched N") (r(N))
}
postclose `SUP'

preserve
use "$DIAG/Table_A6_common_support.dta", clear
export delimited using "$DIAG/Table_A6_common_support.csv", replace
restore

********************************************************************************
* 8. MANUSCRIPT TEXT AND PLACEMENT CHECKLIST
********************************************************************************
file open TXT using "$DIAG/PSM_manuscript_text_and_placement.txt", write replace
file write TXT "PSM SECTION TEXT" _n _n
file write TXT "Table A6 reports treated and control means, standardized mean differences before and after matching, and variance ratios for continuous covariates. The Love plot provides a visual summary using an absolute-SMD benchmark of 0.10. These diagnostics assess balance on observed covariates and do not establish balance on unobserved determinants of venture-debt receipt." _n _n
file write TXT "Figure A1 displays the estimated propensity-score distributions before and after matching. Panel B shows improved overlap, although the distributions are not identical and perfect density overlap is not required. The figure documents overlap in estimated scores; it does not establish conditional independence, eliminate endogeneity, or prove that matching fully resolves comparability." _n _n
file write TXT "PLACEMENT CHECKLIST" _n
file write TXT "1. Cite and discuss Table A6 in the PSM subsection." _n
file write TXT "2. Cite Figure A1 immediately after the common-support discussion." _n
file write TXT "3. Cite the Love plot when discussing standardized balance." _n
file write TXT "4. State explicitly that all diagnostics concern observed covariates only." _n
file write TXT "5. Check that every retained main-text and Appendix table or figure is referenced and serves a stated empirical purpose." _n
file close TXT

log close
