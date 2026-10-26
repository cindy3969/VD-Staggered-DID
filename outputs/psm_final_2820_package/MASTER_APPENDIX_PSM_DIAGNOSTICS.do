version 19
clear all
set more off

global PKG  "C:/Users/user/Documents/VD/outputs/psm_final_2820_package"
global BASE "C:/Users/user/Documents/VD/outputs/psm_rematch_rebuilt"
global OUT  "$PKG/appendix_diagnostics"
capture mkdir "$OUT"

capture log close
log using "$OUT/Appendix_PSM_diagnostics.log", text replace

********************************************************************************
* 0. LOAD THE CORRECTED FULL-SAMPLE PROPENSITY SCORES
********************************************************************************
capture confirm file "$BASE/psm_full7316_with_scores.dta"
if _rc {
    display as error "Required input is missing: $BASE/psm_full7316_with_scores.dta"
    display as error "Run REBUILT_PSM_1410_and_diagnostics.do first."
    exit 601
}

use "$BASE/psm_full7316_with_scores.dta", clear
assert _N==7316
count if vd_backed==1 & psm_matched==1
assert r(N)==1410
count if vd_backed==0 & psm_matched==1
assert r(N)==1410

* Calendar/reference-year diagnostic was not included in the historical score.
gen double reference_year = cond(vd_backed==1,first_vd_year,founding_year+5)
label var reference_year "Actual or pseudo reference year"
label var prior_patent "Prior patent indicator"

********************************************************************************
* 1. TABLE A6: BALANCE BEFORE AND AFTER MATCHING
* Continuous SMD uses pooled pre-match SD as the common denominator.
* Variance ratios are reported for continuous variables only.
********************************************************************************
tab industry2, gen(indcat_)
tab region2, gen(regcat_)

tempname T
postfile `T' str60 covariate str18 variable_type str3 matched_on ///
 double treated_before control_before smd_before variance_ratio_before ///
 treated_after control_after smd_after variance_ratio_after ///
 using "$OUT/Table_A6_balance.dta", replace

local continuous founding_year reference_year time_first_vc funding_rounds_ref ln_funding_ref
foreach v of local continuous {
    local vlabel "`v'"
    if "`v'"=="founding_year"      local vlabel "Founding year"
    if "`v'"=="reference_year"     local vlabel "Actual or pseudo reference year"
    if "`v'"=="time_first_vc"      local vlabel "Years from founding to first VC"
    if "`v'"=="funding_rounds_ref" local vlabel "Number of funding rounds at reference year"
    if "`v'"=="ln_funding_ref"     local vlabel "Log cumulative funding at reference year"
    quietly summarize `v' if vd_backed==1 & psm_esample
    local mt0=r(mean)
    local vt0=r(Var)
    quietly summarize `v' if vd_backed==0 & psm_esample
    local mc0=r(mean)
    local vc0=r(Var)
    local pool=sqrt((`vt0'+`vc0')/2)
    quietly summarize `v' if vd_backed==1 & psm_matched
    local mt1=r(mean)
    local vt1=r(Var)
    quietly summarize `v' if vd_backed==0 & psm_matched
    local mc1=r(mean)
    local vc1=r(Var)
    local used="Yes"
    if "`v'"=="reference_year" local used="No"
    post `T' ("`vlabel'") ("Continuous") ("`used'") ///
        (`mt0') (`mc0') ((`mt0'-`mc0')/`pool') (`vt0'/`vc0') ///
        (`mt1') (`mc1') ((`mt1'-`mc1')/`pool') (`vt1'/`vc1')
}

* Prior patent is a substantively important diagnostic, but was not in the score.
foreach v in prior_patent {
    quietly summarize `v' if vd_backed==1 & psm_esample
    local mt0=r(mean)
    quietly summarize `v' if vd_backed==0 & psm_esample
    local mc0=r(mean)
    local pool=sqrt((`mt0'*(1-`mt0')+`mc0'*(1-`mc0'))/2)
    quietly summarize `v' if vd_backed==1 & psm_matched
    local mt1=r(mean)
    quietly summarize `v' if vd_backed==0 & psm_matched
    local mc1=r(mean)
    post `T' ("`: variable label `v''") ("Binary") ("No") ///
        (`mt0') (`mc0') ((`mt0'-`mc0')/`pool') (.) ///
        (`mt1') (`mc1') ((`mt1'-`mc1')/`pool') (.)
}

* Report categorical balance by level; do not compare arbitrary numeric codes.
foreach stub in indcat regcat {
    unab levels : `stub'_*
    foreach v of local levels {
        quietly summarize `v' if vd_backed==1 & psm_esample
        local mt0=r(mean)
        quietly summarize `v' if vd_backed==0 & psm_esample
        local mc0=r(mean)
        local pool=sqrt((`mt0'*(1-`mt0')+`mc0'*(1-`mc0'))/2)
        quietly summarize `v' if vd_backed==1 & psm_matched
        local mt1=r(mean)
        quietly summarize `v' if vd_backed==0 & psm_matched
        local mc1=r(mean)
        local levelnum = subinstr("`v'","`stub'_","",1)
        if "`stub'"=="indcat" local lab "Industry category `levelnum'"
        if "`stub'"=="regcat" local lab "Region category `levelnum'"
        post `T' ("`lab'") ("Categorical level") ("Yes") ///
            (`mt0') (`mc0') (cond(`pool'>0,(`mt0'-`mc0')/`pool',0)) (.) ///
            (`mt1') (`mc1') (cond(`pool'>0,(`mt1'-`mc1')/`pool',0)) (.)
    }
}
postclose `T'

use "$OUT/Table_A6_balance.dta", clear
replace covariate="Founding year" if covariate==""
replace covariate="Actual or pseudo reference year" if covariate=="reference_year"
gen abs_smd_before=abs(smd_before)
gen abs_smd_after=abs(smd_after)
gen byte exceeds_010_after=abs_smd_after>.10 if !missing(abs_smd_after)
format treated_before control_before treated_after control_after %9.3f
format smd_before smd_after variance_ratio_before variance_ratio_after %9.3f
export delimited using "$OUT/Table_A6_balance.csv", replace

display as text _newline "TABLE A6. COVARIATE BALANCE BEFORE AND AFTER MATCHING"
list covariate matched_on treated_before control_before smd_before ///
 variance_ratio_before treated_after control_after smd_after ///
 variance_ratio_after, noobs clean abbreviate(34)

quietly summarize abs_smd_after, meanonly
display as result "Maximum absolute SMD after matching = " %6.3f r(max)
count if exceeds_010_after==1
display as result "Rows with |SMD| > .10 after matching = " r(N)

********************************************************************************
* 2. FIGURE A2: LOVE PLOT
********************************************************************************
gsort -abs_smd_before
gen plot_order=_n
gen str60 plot_label=covariate
forvalues i=1/`=_N' {
    local lab=plot_label[`i']
    label define balorder `i' "`lab'", add
}
label values plot_order balorder

twoway ///
 (scatter plot_order abs_smd_before, msymbol(O) mcolor(maroon)) ///
 (scatter plot_order abs_smd_after, msymbol(D) mcolor(navy)), ///
 xline(.10, lpattern(dash) lcolor(gs7)) ///
 ylabel(1(1)`=_N', valuelabel angle(horizontal) labsize(vsmall)) ///
 xlabel(0(.1).5, format(%3.1f)) ///
 xtitle("Absolute standardized mean difference") ytitle("") ///
 title("Covariate balance before and after matching") ///
 legend(order(1 "Before matching" 2 "After matching") rows(1) position(6)) ///
 graphregion(color(white)) plotregion(color(white)) name(LOVE_APPENDIX, replace)
graph export "$OUT/Figure_A2_Love_plot.png", replace width(3000)
graph save "$OUT/Figure_A2_Love_plot.gph", replace

********************************************************************************
* 3. FIGURE A1: PROPENSITY-SCORE OVERLAP
* Density overlap is descriptive and is not evidence of balance on unobservables.
********************************************************************************
use "$BASE/psm_full7316_with_scores.dta", clear
twoway ///
 (kdensity _pscore if vd_backed==1 & psm_esample, lcolor(maroon) lwidth(medthick)) ///
 (kdensity _pscore if vd_backed==0 & psm_esample, lcolor(navy) lpattern(dash) lwidth(medthick)), ///
 title("Panel A. Before matching") xtitle("Estimated propensity score") ytitle("Density") ///
 legend(order(1 "VD-backed" 2 "VC-only")) graphregion(color(white)) name(OVERLAP_PRE, replace)

twoway ///
 (kdensity _pscore if vd_backed==1 & psm_matched, lcolor(maroon) lwidth(medthick)) ///
 (kdensity _pscore if vd_backed==0 & psm_matched, lcolor(navy) lpattern(dash) lwidth(medthick)), ///
 title("Panel B. After 1:1 matching") xtitle("Estimated propensity score") ytitle("Density") ///
 legend(order(1 "VD-backed" 2 "Matched VC-only")) graphregion(color(white)) name(OVERLAP_POST, replace)

graph combine OVERLAP_PRE OVERLAP_POST, cols(2) ///
 title("Propensity-score distributions before and after matching") ///
 graphregion(color(white)) name(FIG_A1, replace)
graph export "$OUT/Figure_A1_propensity_score_overlap.png", replace width(3600)
graph save "$OUT/Figure_A1_propensity_score_overlap.gph", replace

********************************************************************************
* 4. COMMON-SUPPORT TABLE
********************************************************************************
quietly summarize _pscore if vd_backed==1 & psm_esample, meanonly
scalar tmin=r(min)
scalar tmax=r(max)
quietly summarize _pscore if vd_backed==0 & psm_esample, meanonly
scalar cmin=r(min)
scalar cmax=r(max)
scalar lower=max(tmin,cmin)
scalar upper=min(tmax,cmax)
gen byte empirical_overlap=inrange(_pscore,lower,upper) if psm_esample

tempname S
postfile `S' str56 statistic double value using "$OUT/Table_A6_common_support.dta", replace
post `S' ("Treated propensity-score minimum") (tmin)
post `S' ("Treated propensity-score maximum") (tmax)
post `S' ("Control propensity-score minimum") (cmin)
post `S' ("Control propensity-score maximum") (cmax)
post `S' ("Empirical common-support lower bound") (lower)
post `S' ("Empirical common-support upper bound") (upper)
foreach g in 0 1 {
    quietly count if vd_backed==`g' & psm_esample
    post `S' ("Group `g': propensity-score estimation N") (r(N))
    quietly count if vd_backed==`g' & psm_esample & empirical_overlap==1
    post `S' ("Group `g': within empirical overlap N") (r(N))
    quietly count if vd_backed==`g' & psm_esample & empirical_overlap==0
    post `S' ("Group `g': outside empirical overlap N") (r(N))
    quietly count if vd_backed==`g' & psm_matched
    post `S' ("Group `g': final matched N") (r(N))
}
postclose `S'

use "$OUT/Table_A6_common_support.dta", clear
export delimited using "$OUT/Table_A6_common_support.csv", replace
display as text _newline "COMMON-SUPPORT INFORMATION"
list, noobs clean

log close
exit, clear
