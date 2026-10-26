version 19
clear all
set more off

global ROOT "C:/Users/user/Documents/VD/outputs/psm_final_2820_package"
import delimited using "$ROOT/historical_weight_balance_diagnostics_6vars.csv", clear varnames(1)

gen order = _n
gen y = _N - order + 1
gen before = abs(pre_smd)
gen after  = abs(post_smd)

label define covlbl ///
10 "Log funding amount at reference year" ///
9  "Funding rounds at reference year" ///
8  "Founding year" ///
7  "Time to first VC" ///
6  "Region: California" ///
5  "Region: Massachusetts" ///
4  "Region: New York" ///
3  "Industry: Bio/Healthcare" ///
2  "Industry: Hardware/Manufacturing/DeepTech" ///
1  "Industry: Software/IT services"
label values y covlbl

twoway ///
    (scatter y before, msymbol(O) mcolor(maroon) msize(medsmall)) ///
    (scatter y after,  msymbol(D) mcolor(navy)   msize(medsmall)), ///
    xline(10, lpattern(dash) lcolor(gs8)) ///
    ylabel(1(1)10, valuelabel angle(0) labsize(small)) ///
    xlabel(0(10)60, labsize(small)) ///
    xtitle("Absolute standardized mean difference (%)") ///
    ytitle("") ///
    title("Covariate balance before and after matching") ///
    subtitle("Existing 2,820-firm sample identified by weight = 1") ///
    legend(order(1 "Before matching" 2 "After matching") rows(1) position(6)) ///
    graphregion(color(white)) plotregion(color(white)) ///
    name(LOVE_EXISTING_WEIGHT, replace)

graph export "$ROOT/love_plot_existing_weight_6vars.png", replace width(3000)
graph save "$ROOT/love_plot_existing_weight_6vars.gph", replace

list covariate pre_smd post_smd pre_variance_ratio post_variance_ratio, noobs clean
