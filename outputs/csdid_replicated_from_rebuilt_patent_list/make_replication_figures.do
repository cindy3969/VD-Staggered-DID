version 19
clear all
set more off
global R "C:/Users/user/Documents/VD/outputs/csdid_replicated_from_rebuilt_patent_list"
graph set window fontface "Times New Roman"
graph set print fontface "Times New Roman"

import delimited "$R/Figure_1a_raw_trajectories_data.csv", clear varnames(1)
twoway ///
 (connected mean event_time if comparison=="Never treated" & group=="VD-backed", sort msymbol(O) lcolor(navy) mcolor(navy)) ///
 (connected mean event_time if comparison=="Never treated" & group=="Control", sort msymbol(S) lpattern(dash) lcolor(maroon) mcolor(maroon)), ///
 xline(-0.5, lpattern(dash) lcolor(gs8)) xlabel(-4(1)4) ytitle("Mean granted applications per firm-year") ///
 xtitle("Years relative to first venture debt") title("Never-treated comparison") ///
 legend(order(1 "VD-backed" 2 "Control")) name(RAW_NEVER, replace)
graph save "$R/raw_never.gph", replace
twoway ///
 (connected mean event_time if comparison=="Not-yet treated" & group=="VD-backed", sort msymbol(O) lcolor(navy) mcolor(navy)) ///
 (connected mean event_time if comparison=="Not-yet treated" & group=="Control", sort msymbol(S) lpattern(dash) lcolor(maroon) mcolor(maroon)), ///
 xline(-0.5, lpattern(dash) lcolor(gs8)) xlabel(-4(1)4) ytitle("Mean granted applications per firm-year") ///
 xtitle("Years relative to first venture debt") title("Not-yet-treated comparison") ///
 legend(order(1 "VD-backed" 2 "Control")) name(RAW_NOTYET, replace)
graph save "$R/raw_notyet.gph", replace
graph combine "$R/raw_never.gph" "$R/raw_notyet.gph", cols(2) title("Figure 1a. Cohort-aligned outcome trajectories") name(FIG1A, replace)
graph export "$R/Figure_1a_raw_trajectories.png", replace width(3600)

import delimited "$R/Figure_1b_dynamic_ATT_data.csv", clear varnames(1)
twoway (rcap conf_low conf_high event_time, lcolor(navy)) ///
       (connected estimate event_time, sort msymbol(O) lcolor(navy) mcolor(navy)), ///
 yline(0, lcolor(gs8)) xline(-0.5, lpattern(dash) lcolor(gs8)) xlabel(-4(1)4) ///
 xtitle("Years relative to first venture debt") ytitle("ATT on annual granted applications") ///
 title("Figure 1b. Dynamic Callaway-Sant'Anna ATT") legend(off) name(FIG1B, replace)
graph export "$R/Figure_1b_dynamic_ATT.png", replace width(3000)
exit, clear
