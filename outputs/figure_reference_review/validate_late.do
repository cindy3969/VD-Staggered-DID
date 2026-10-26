version 19
clear all
set more off
set linesize 255
log using "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected/Figure_late_validation.log", text replace
use "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected/firm_year_all_applications_and_truncation_specs.dta", clear
keep if year<=2024
drop if missing(grantedapp_norm, ln1p_cum_funding_l1, cum_funding_rounds_l1, region_fe, industry_fe, full_firm_id, year, G)
* (5) Late stage
********************************************************************************
display as result "(5) Late stage"
quietly count if (G==0 | early==0)
scalar eligible_observations = r(N)
egen byte firm_tag = tag(full_firm_id) if (G==0 | early==0)
quietly count if firm_tag==1
scalar eligible_firms = r(N)
drop firm_tag

quietly csdid grantedapp_norm ///
    ln1p_cum_funding_l1 cum_funding_rounds_l1 ///
    i.region_fe i.industry_fe if (G==0 | early==0), ///
    ivar(full_firm_id) time(year) gvar(G) method(dripw)

csdid_estat simple

* Event-study estimates followed immediately by their graph.
csdid_estat event, window(-4 4)
csdid_plot, yline(0, lcolor(gs8)) xline(0, lpattern(dash)) ///
    xtitle("Years relative to first VD") ///
    ytitle("ATT on normalized granted applications") ///
    title("(5) Late stage") ///
    graphregion(color(white)) name(Event_Late, replace)

* Keep the aggregated event estimates, not the underlying ATT(g,t) matrix.
matrix fig_late_b = r(b)
matrix fig_late_V = r(V)

csdid_estat group
display as text "Observations (complete-case input): " as result %12.0fc eligible_observations
display as text "Firms (complete-case input):        " as result %12.0fc eligible_firms
display as text "Control group: Never-treated"



log close
exit, clear
