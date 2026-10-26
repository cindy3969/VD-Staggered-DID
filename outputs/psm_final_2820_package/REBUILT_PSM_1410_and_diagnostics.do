version 19
clear all
set more off
set seed 20261011

global ROOT "C:/Users/user/Documents/VD/outputs/psm_rematch_rebuilt"
global DATA "C:/Users/user/Documents/VD/outputs/csdid_ultimately_granted_primary/csdid_ultimately_granted_full7316_controls.dta"

capture log close
log using "$ROOT/PSM_1410_and_diagnostics.log", text replace
use "$DATA", clear
assert _N==7316
count if vd_backed==1
assert r(N)==1440

capture which psmatch2
if _rc {
    display as error "psmatch2 is not installed"
    exit 199
}

********************************************************************************
* Historical reference-year PSM: 1 nearest neighbor, no replacement.
* The 30 VD firms with missing reference-year funding are excluded by e(sample),
* leaving 1,410 treated firms available for matching.
********************************************************************************
psmatch2 vd_backed i.founding_year ib4.industry2 funding_rounds_ref ///
    ln_funding_ref ib4.region2 time_first_vc, neighbor(1) logit noreplacement

gen byte psm_esample=!missing(_pscore)
gen byte psm_matched=(_weight>0 & !missing(_weight))
replace psm_matched=1 if vd_backed==1 & psm_esample==1

count if vd_backed==1 & psm_esample
assert r(N)==1410
count if vd_backed==1 & psm_matched
assert r(N)==1410
count if vd_backed==0 & psm_matched
assert r(N)==1410

save "$ROOT/psm_full7316_with_scores.dta", replace
export delimited using "$ROOT/psm_full7316_with_scores.csv", replace
preserve
    keep if psm_matched
    save "$ROOT/psm_matched_2820.dta", replace
    export delimited using "$ROOT/psm_matched_2820.csv", replace
restore

********************************************************************************
* Common support and overlap.
********************************************************************************
quietly summarize _pscore if vd_backed==1 & psm_esample, meanonly
scalar tmin=r(min)
scalar tmax=r(max)
quietly summarize _pscore if vd_backed==0 & psm_esample, meanonly
scalar cmin=r(min)
scalar cmax=r(max)
scalar lower=max(tmin,cmin)
scalar upper=min(tmax,cmax)
gen byte overlap=inrange(_pscore,lower,upper) if psm_esample

tempname C
postfile `C' str52 metric double value using "$ROOT/common_support.dta", replace
post `C' ("Treated propensity-score minimum") (tmin)
post `C' ("Treated propensity-score maximum") (tmax)
post `C' ("Control propensity-score minimum") (cmin)
post `C' ("Control propensity-score maximum") (cmax)
post `C' ("Common-support lower bound") (lower)
post `C' ("Common-support upper bound") (upper)
foreach g in 0 1 {
    quietly count if vd_backed==`g' & psm_esample
    post `C' ("Group `g': estimation N") (r(N))
    quietly count if vd_backed==`g' & psm_esample & overlap==1
    post `C' ("Group `g': in empirical overlap N") (r(N))
    quietly count if vd_backed==`g' & psm_esample & overlap==0
    post `C' ("Group `g': outside empirical overlap N") (r(N))
    quietly count if vd_backed==`g' & psm_matched
    post `C' ("Group `g': matched N") (r(N))
}
postclose `C'

twoway ///
 (kdensity _pscore if vd_backed==1 & psm_esample, lcolor(maroon)) ///
 (kdensity _pscore if vd_backed==0 & psm_esample, lcolor(navy) lpattern(dash)), ///
 title("Before matching") xtitle("Estimated propensity score") ytitle("Density") ///
 legend(order(1 "VD-backed" 2 "VC-only")) graphregion(color(white)) name(PRE, replace)
twoway ///
 (kdensity _pscore if vd_backed==1 & psm_matched, lcolor(maroon)) ///
 (kdensity _pscore if vd_backed==0 & psm_matched, lcolor(navy) lpattern(dash)), ///
 title("After 1:1 matching") xtitle("Estimated propensity score") ytitle("Density") ///
 legend(order(1 "VD-backed" 2 "Matched VC-only")) graphregion(color(white)) name(POST, replace)
graph combine PRE POST, cols(2) title("Propensity-score overlap") graphregion(color(white))
graph export "$ROOT/Figure_PScore_overlap.png", replace width(3600)

********************************************************************************
* Standardized mean differences and variance ratios.
********************************************************************************
tab industry2, gen(ind_)
tab region2, gen(reg_)
tempname B
postfile `B' str60 covariate str18 type double mean_t_before mean_c_before ///
 smd_before vr_before mean_t_after mean_c_after smd_after vr_after ///
 using "$ROOT/psm_balance.dta", replace

foreach v in founding_year funding_rounds_ref ln_funding_ref time_first_vc {
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
    post `B' ("`v'") ("Continuous") (`mt0') (`mc0') ((`mt0'-`mc0')/`pool') (`vt0'/`vc0') ///
        (`mt1') (`mc1') ((`mt1'-`mc1')/`pool') (`vt1'/`vc1')
}

foreach stub in ind reg {
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
        local lab : variable label `v'
        post `B' ("`lab'") ("Categorical level") (`mt0') (`mc0') ///
            (cond(`pool'>0,(`mt0'-`mc0')/`pool',0)) (.) (`mt1') (`mc1') ///
            (cond(`pool'>0,(`mt1'-`mc1')/`pool',0)) (.)
    }
}
postclose `B'

use "$ROOT/psm_balance.dta", clear
gen abs_smd_before=abs(smd_before)
gen abs_smd_after=abs(smd_after)
gen exceeds_010_after=abs_smd_after>.10
gsort -abs_smd_before
gen order=_n
gen str60 plot_label=covariate
replace plot_label="Founding year" if covariate=="founding_year"
replace plot_label="Funding rounds at reference year" if covariate=="funding_rounds_ref"
replace plot_label="Log funding at reference year" if covariate=="ln_funding_ref"
replace plot_label="Years to first VC" if covariate=="time_first_vc"
forvalues i=1/`=_N' {
    local text=plot_label[`i']
    label define orderlbl `i' "`text'", add
}
label values order orderlbl
export delimited using "$ROOT/psm_balance.csv", replace
twoway ///
 (scatter order abs_smd_before, msymbol(O) mcolor(maroon)) ///
 (scatter order abs_smd_after, msymbol(D) mcolor(navy)), ///
 xline(.10, lpattern(dash) lcolor(gs7)) ///
 ylabel(1(1)`=_N', valuelabel angle(horizontal) labsize(vsmall)) ///
 xtitle("Absolute standardized mean difference") ytitle("") ///
 title("Covariate balance before and after 1:1 matching") ///
 legend(order(1 "Before matching" 2 "After matching") rows(1) position(6)) ///
 graphregion(color(white))
graph export "$ROOT/Figure_Love_plot.png", replace width(2800)
graph save "$ROOT/Figure_Love_plot.gph", replace

quietly summarize abs_smd_before, meanonly
display as result "Maximum |SMD| before = " %7.3f r(max)
quietly summarize abs_smd_after, meanonly
display as result "Maximum |SMD| after  = " %7.3f r(max)
count if exceeds_010_after
display as result "Balance rows above .10 after matching = " r(N)

use "$ROOT/common_support.dta", clear
export delimited using "$ROOT/common_support.csv", replace
list, noobs clean
log close
exit, clear
