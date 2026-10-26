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
    gen double founding_year=Founding_Year
    keep name_key reference_year founding_year
    bysort name_key: egen reference_min=min(reference_year)
    bysort name_key: egen reference_max=max(reference_year)
    bysort name_key: egen founding_min=min(founding_year)
    bysort name_key: egen founding_max=max(founding_year)
    assert reference_min==reference_max
    assert founding_min==founding_max
    bysort name_key: keep if _n==1
    drop reference_min reference_max founding_min founding_max
    save `firm_reference', replace

    import delimited using "$APPUNION", clear varnames(1) encoding(utf8)
    keep if inrange(filing_year,2010,2024)
    duplicates drop full_firm_id application_id, force
    count
    assert r(N)==39249
    gen str244 name_key=ustrlower(organization_name)
    replace name_key=ustrregexra(name_key,"[^a-z0-9]","")
    merge m:1 name_key using `firm_reference', keep(match) nogen
    * Exclude applications filed before the firm's founding year.  The PSM
    * patent-history covariate is the count from founding through VD year.
    gen byte app_at_vd=inrange(filing_year,founding_year,reference_year)
    gen byte app_win3=inrange(filing_year-reference_year,0,3)
    collapse (sum) priorpatent_VD_2=app_at_vd ///
                   patent_application_win3=app_win3, by(name_key)
    save `application_counts', replace
restore

capture drop patent_application_VD priorpatent_VD_2 priorpatentdummy_VD patent_application_win3 name_key
gen str244 name_key=ustrlower(OrganizationName)
replace name_key=ustrregexra(name_key,"[^a-z0-9]","")
merge m:1 name_key using `application_counts', keep(master match) gen(_merge_appcounts)
replace priorpatent_VD_2=0 if missing(priorpatent_VD_2)
replace patent_application_win3=0 if missing(patent_application_win3)
gen double patent_application_VD=priorpatent_VD_2
gen byte priorpatentdummy_VD=(priorpatent_VD_2>0)
label var priorpatent_VD_2 "Applications filed from founding through actual or hypothetical VD year"
label var patent_application_VD "Alias of priorpatent_VD_2 for backward compatibility"
label var priorpatentdummy_VD "Any application filed from founding through reference year"
label var patent_application_win3 "Applications filed in years t=0 to t+3"

assert priorpatent_VD_2==9 if OrganizationName=="Affirmed Networks"
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
    priorpatent_VD_2 ///
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
         Grant_3years priorpatent_VD_2 priorpatentdummy_VD ///
         patent_application_VD patent_application_win3 ///
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

****Variables construction
***variables
rename Founding_Year Foundingyear
rename VDYear VDyear
*********************APPENDIX********************
* Table A6: 매칭 전후 balance
pstest Foundingyear VDyear TimeToFirst_VC ///
    NumberOfFunding_Rounds_FirstVD ///
    ln_Total_Funding_Amount_FirstVD priorpatent_VD_2 ///
    Region2 Industry2, both

* Figure A1: PROPENSITY-SCORE OVERLAP BEFORE AND AFTER MATCHING
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


* Figure A2. PSM loveplot
pstest Foundingyear VDyear TimeToFirst_VC ///
    NumberOfFunding_Rounds_FirstVD ///
    ln_Total_Funding_Amount_FirstVD priorpatent_VD_2 ///
    Region2 Industry2, both graph

graph export "$DIAG/Figure_A2_Love_plot.png", replace width(3000)
graph save "$DIAG/Figure_A2_Love_plot.gph", replace

* Table A7. COMMON-SUPPORT INFORMATION
quietly summarize _pscore if VD_Backing == 1 ///
    & _weight > 0 & _weight < ., meanonly
scalar treated_min = r(min)
scalar treated_max = r(min)

quietly summarize _pscore if VD_Backing == 0 ///
    & _weight > 0 & _weight < ., meanonly
scalar control_min = r(min)
scalar control_max = r(min)


capture drop psm_esample
gen byte psm_esample = !missing(_pscore, VD_Backing)

capture drop empirical_support
gen byte empirical_support = ///
    inrange(_pscore, support_lower, support_upper) if psm_esample

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
format value %12.4f
list statistic value, noobs clean
restore

tab VD_Backing _support if psm_esample, missing


