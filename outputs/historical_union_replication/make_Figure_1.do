version 18
clear all
set more off
global OUT "C:/Users/user/Documents/VD/outputs/historical_union_replication"
graph set window fontface "Times New Roman"
graph set print fontface "Times New Roman"

import delimited using "$OUT/Figure_1a_historical_raw_trajectories.csv", clear
twoway ///
 (connected treated event_time, sort msymbol(O) lcolor(cranberry) mcolor(cranberry)) ///
 (connected never_control event_time, sort msymbol(S) lcolor(navy) mcolor(navy)), ///
 xline(-.5, lpattern(dash) lcolor(gs8)) xlabel(-4(1)4) ///
 xtitle("Event time (t - G)") ytitle("Granted patent applications per firm-year") ///
 title("(a) Mean plots: never-treated comparison") ///
 legend(order(1 "VD-backed (treated)" 2 "Never VD (control)") rows(1)) ///
 graphregion(color(white)) name(F1A, replace)
graph save "$OUT/Figure_1a_historical.gph", replace

import delimited using "$OUT/Figure_1b_historical_dynamic_ATT.csv", clear
twoway ///
 (rcap conf_low conf_high event_time, lcolor(navy)) ///
 (connected att event_time, sort msymbol(O) lcolor(navy) mcolor(navy)), ///
 yline(0, lcolor(gs8)) xline(-.5, lpattern(dash) lcolor(gs8)) xlabel(-4(1)4) ///
 xtitle("Event time (t - G)") ytitle("ATT on granted patent applications") ///
 title("(b) Callaway-Sant'Anna dynamic ATT") legend(off) ///
 graphregion(color(white)) name(F1B, replace)
graph save "$OUT/Figure_1b_historical.gph", replace

graph combine "$OUT/Figure_1a_historical.gph" "$OUT/Figure_1b_historical.gph", ///
 cols(2) title("Figure 1. Diagnostic analysis for the staggered DiD design") ///
 graphregion(color(white))
graph export "$OUT/Figure_1_historical_union_replication.png", replace width(3600)
graph save "$OUT/Figure_1_historical_union_replication.gph", replace
