clear all
set more off
use "C:/Users/user/Documents/VD/260122 winsorization_stage4.dta", clear
local y ln_patentbyfiling_win3
local controls patentdummybyfiling ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
local sample inrange(stage4,1,4)
tempfile m1 m2 m2clean sep

reg `y' i.VD##ib1.stage4 `controls' if `sample'
margins stage4, dydx(VD) saving(`m1', replace)

reg `y' i.VD##ib1.stage4 i.VD##ib0.patentdummybyfiling ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2 if `sample'
margins stage4, dydx(VD) saving(`m2', replace)

tempname ph
postfile `ph' str32 model byte stage4 double effect se p_value ci_low ci_high n df_r using `sep', replace
forvalues j=1/4 {
    quietly reg `y' VD `controls' if stage4==`j'
    scalar eff = _b[VD]
    scalar serr = _se[VD]
    scalar dfr = e(df_r)
    scalar pv = 2*ttail(dfr,abs(eff/serr))
    scalar lo = eff-invttail(dfr,.025)*serr
    scalar hi = eff+invttail(dfr,.025)*serr
    post `ph' ("separate_stage_regression") (`j') (eff) (serr) (pv) (lo) (hi) (e(N)) (dfr)
}
postclose `ph'

use `m1', clear
gen str32 model = "interaction_margins"
rename _margin effect
rename _se se
rename _pvalue p_value
rename _ci_lb ci_low
rename _ci_ub ci_high
gen double n = 2720
gen double df_r = 2702
keep model stage4 effect se p_value ci_low ci_high n df_r
save `m1', replace
use `m2', clear
gen str32 model = "interaction_full_margins"
rename _margin effect
rename _se se
rename _pvalue p_value
rename _ci_lb ci_low
rename _ci_ub ci_high
gen double n = 2720
gen double df_r = 2701
keep model stage4 effect se p_value ci_low ci_high n df_r
save `m2clean', replace
use `m1', clear
append using `m2clean'
append using `sep'
label define stage4lbl 1 "Seed" 2 "Series A" 3 "Series B" 4 "Series C+", replace
label values stage4 stage4lbl
decode stage4, gen(stage)
order model stage stage4 effect se p_value ci_low ci_high n df_r
sort model stage4
export delimited using "C:/Users/user/Documents/VD/stage_specific_H3_results.csv", replace
save "C:/Users/user/Documents/VD/stage_specific_H3_results.dta", replace
exit, clear
