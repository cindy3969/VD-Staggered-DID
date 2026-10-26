version 19
clear all
set more off
global ROOT "C:/Users/user/Documents/VD/outputs/psm_final_2820_package"
global OUT "C:/Users/user/Documents/VD/outputs/downstream_financing"
log using "$OUT/validation.log", text replace
use "$ROOT/table3_original_2820_cross_section_v2.dta", clear

* Original 260122 winsorization variables are identical for all 2820 firms.
* Reproduce legacy specifications separately from revised definitions below.
* The existing Table 6 mixes all-financing t1/t2 and equity t3; it is NOT
* an exact replication of ln_moneyraised_y1/y2/y3. Table 7 below also uses
* different exit dates/status and some non-factor categorical controls.
preserve
use "$ROOT/table3_original_2820_cross_section_v2.dta", clear
forvalues h=1/3 {
    reghdfe ln_moneyraised_y`h' VD i.patentdummybyfiling i.earlystage ///
        ln_MoneyRaised_VD NumofFundingRounds_VD, ///
        absorb(Region2 Industry2 Foundingyear) vce(robust)
    estimates store legacy6_`h'
}
esttab legacy6_1 legacy6_2 legacy6_3 using "$OUT/Table6_legacy_replication.csv", ///
    replace b(6) se(6) stats(N r2)
local j=0
foreach event in acq3 public3 badexit3 {
    stset VDage3, failure(`event'==1) id(firm_id)
    stcox VD i.Region2 i.Industry2 i.Foundingyear, nohr
    local ++j
    estimates store legacy7_`j'
    stcox VD patentdummybyfiling earlystage ln_MoneyRaised_VD ///
        NumofFundingRounds_VD i.Region2 i.Industry2 i.Foundingyear, nohr
    local ++j
    estimates store legacy7_`j'
}
esttab legacy7_1 legacy7_2 legacy7_3 legacy7_4 legacy7_5 legacy7_6 ///
    using "$OUT/Table7_legacy_replication.csv", replace b(6) se(6) stats(N N_fail)
restore
* Four supporting estimands; separate outputs, no changes to innovation outcomes.
version 19
* Financing support analysis embedded directly in this master do-file.
* Supporting evidence, not a mediation test. Post-treatment selection affects amounts.
* Build data with scripts/build_downstream_financing.py after updating source/cutoff.
preserve
local D "C:/Users/user/Documents/VD/outputs/downstream_financing"
use "`D'/financing_support.dta", clear
isid firm_id
assert _N == 2820
local X "VD i.patentdummybyfiling i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD"
local FE "i.Region2 i.Industry2 i.Foundingyear"
display as text "SUPPORT ONLY: year-end reference, assumed coverage through 2023-12-31."
display as text "Not exact time since VD; no competing-exit adjustment."
tempname P
postfile `P' str32 model double b se N using "`D'/support_estimates.dta", replace
* 1. Cumulative next-round probability at fixed horizons, robust LPM.
* 4. ln(1 + cumulative USD), retaining no-round zeros under cutoff assumption.
forvalues h=1/3 {
    assert missing(raise`h') if complete`h' == 0
    assert missing(cum`h') if undisclosed`h' == 1
    reghdfe raise`h' `X', absorb(Region2 Industry2 Foundingyear) vce(robust)
    post `P' ("probability_`h'y") (_b[VD]) (_se[VD]) (e(N))
    estimates save "`D'/probability_`h'y.ster", replace
    gen double ln_cum_usd`h' = ln(1 + cum`h')
    assert ln_cum_usd`h' == 0 if cum`h' == 0
    assert missing(ln_cum_usd`h') if missing(cum`h')
    reghdfe ln_cum_usd`h' `X', absorb(Region2 Industry2 Foundingyear) vce(robust)
    estimates store logcum`h'
    post `P' ("cumulative_log1p_USD_`h'y") (_b[VD]) (_se[VD]) (e(N))
    estimates save "`D'/cumulative_`h'y.ster", replace
}
esttab logcum1 logcum2 logcum3 using "`D'/Panel_C_log_cumulative.csv", ///
    replace b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    stats(N r2 r2_a) title("Cumulative Equity Raised: ln(1 + USD)")
* 1. Next-round hazard. Common three-year follow-up cap; retain censored firms.
gen double stop3 = mdy(12,31,VDyear+3)-mdy(12,31,VDyear)
gen double surv_days = min(duration_days,1095) if observed == 1
gen byte event3 = next_event == 1 & next_days <= stop3 if observed == 1
gen byte surv_event = next_event == 1 & next_days <= 1095 if observed == 1
stset surv_days if observed == 1, failure(surv_event==1) id(firm_id)
stcox `X' `FE', nohr vce(robust)
post `P' ("next_round_log_hazard") (_b[VD]) (_se[VD]) (e(N))
estimates save "`D'/next_round_cox.ster", replace
* 2. Timing: KM survival and restricted mean waiting time, including censoring.
* RMST has a common 1095-day restriction and is unadjusted/descriptive;
* Weibull AFT log-time coefficient is parametric.
sts list, by(VD) at(365 730 1095)
stci, by(VD) rmean
sts graph, by(VD) xtitle("Days since end of VD/reference year") ///
    ytitle("Probability of no subsequent equity round") ///
    title("Supporting financing environment: next equity round")
graph export "`D'/next_equity_survival.png", replace
streg `X' `FE', distribution(weibull) time vce(robust)
post `P' ("waiting_time_weibull_logtime") (_b[VD]) (_se[VD]) (e(N))
estimates save "`D'/waiting_time_aft.ster", replace
* 3. First next-round amount conditional on raising within 3 years.
* Complete 3-year cohorts only; unknown amounts and ambiguous tied rounds excluded.
gen double ln_next_amount = ln(next_amount) if next_amount > 0 & !missing(next_amount)
reghdfe ln_next_amount `X' if complete3==1 & event3==1 & next_n==1, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
post `P' ("conditional_next_round_logUSD") (_b[VD]) (_se[VD]) (e(N))
estimates save "`D'/conditional_next_amount.ster", replace
postclose `P'
use "`D'/support_estimates.dta", clear
export delimited using "`D'/support_estimates.csv", replace
restore


display "FINANCING_VALIDATION_COMPLETE"
log close
