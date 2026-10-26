version 19
clear all
set more off
set linesize 255
capture log close _all
log using "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected/MASTER_csdid_all_applications.log", replace text

* Table 11: Callaway-Sant'Anna DRIPW. DV: grantedapp_norm (NOT log).
* Existing subgroup definitions and covariates are retained.
* Read/filter once. Each model uses an if condition without deleting subgroups.
* Counts describe complete-case input; individual ATT(g,t) samples can differ.
* Graphs are displayed only. No Excel, graph files, or datasets are saved.

use "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected/firm_year_all_applications_and_truncation_specs.dta", clear
keep if year<=2024
drop if missing(grantedapp_norm, ln1p_cum_funding_l1, cum_funding_rounds_l1, region_fe, industry_fe, full_firm_id, year, G)
isid full_firm_id year
xtset full_firm_id year

********************************************************************************
* (1) All firms
********************************************************************************
display as result "(1) All firms"
quietly count
scalar eligible_observations = r(N)
egen byte firm_tag = tag(full_firm_id)
quietly count if firm_tag==1
scalar eligible_firms = r(N)
drop firm_tag

quietly csdid grantedapp_norm ///
    ln1p_cum_funding_l1 cum_funding_rounds_l1 ///
    i.region_fe i.industry_fe, ///
    ivar(full_firm_id) time(year) gvar(G) method(dripw)

csdid_estat simple

* Event-study estimates followed immediately by their graph.
csdid_estat event, window(-4 4)
csdid_plot, yline(0, lcolor(gs8)) xline(0, lpattern(dash)) ///
    xtitle("Years relative to first VD") ///
    ytitle("ATT on normalized granted applications") ///
    title("(1) All firms") ///
    graphregion(color(white)) name(Event_All, replace)

csdid_estat group
display as text "Observations (complete-case input): " as result %12.0fc eligible_observations
display as text "Firms (complete-case input):        " as result %12.0fc eligible_firms
display as text "Control group: Never-treated"

********************************************************************************
* (2) No prior patent
********************************************************************************
display as result "(2) No prior patent"
quietly count if (G==0 | prior==0)
scalar eligible_observations = r(N)
egen byte firm_tag = tag(full_firm_id) if (G==0 | prior==0)
quietly count if firm_tag==1
scalar eligible_firms = r(N)
drop firm_tag

quietly csdid grantedapp_norm ///
    ln1p_cum_funding_l1 cum_funding_rounds_l1 ///
    i.region_fe i.industry_fe if (G==0 | prior==0), ///
    ivar(full_firm_id) time(year) gvar(G) method(dripw)

csdid_estat simple

* Event-study estimates followed immediately by their graph.
csdid_estat event, window(-4 4)
csdid_plot, yline(0, lcolor(gs8)) xline(0, lpattern(dash)) ///
    xtitle("Years relative to first VD") ///
    ytitle("ATT on normalized granted applications") ///
    title("(2) No prior patent") ///
    graphregion(color(white)) name(Event_NoPrior, replace)

csdid_estat group
display as text "Observations (complete-case input): " as result %12.0fc eligible_observations
display as text "Firms (complete-case input):        " as result %12.0fc eligible_firms
display as text "Control group: Never-treated"

********************************************************************************
* (3) Prior patent
********************************************************************************
display as result "(3) Prior patent"
quietly count if (G==0 | prior==1)
scalar eligible_observations = r(N)
egen byte firm_tag = tag(full_firm_id) if (G==0 | prior==1)
quietly count if firm_tag==1
scalar eligible_firms = r(N)
drop firm_tag

quietly csdid grantedapp_norm ///
    ln1p_cum_funding_l1 cum_funding_rounds_l1 ///
    i.region_fe i.industry_fe if (G==0 | prior==1), ///
    ivar(full_firm_id) time(year) gvar(G) method(dripw)

csdid_estat simple

* Event-study estimates followed immediately by their graph.
csdid_estat event, window(-4 4)
csdid_plot, yline(0, lcolor(gs8)) xline(0, lpattern(dash)) ///
    xtitle("Years relative to first VD") ///
    ytitle("ATT on normalized granted applications") ///
    title("(3) Prior patent") ///
    graphregion(color(white)) name(Event_Prior, replace)

csdid_estat group
display as text "Observations (complete-case input): " as result %12.0fc eligible_observations
display as text "Firms (complete-case input):        " as result %12.0fc eligible_firms
display as text "Control group: Never-treated"

********************************************************************************
* (4) Early stage
********************************************************************************
display as result "(4) Early stage"
quietly count if (G==0 | early==1)
scalar eligible_observations = r(N)
egen byte firm_tag = tag(full_firm_id) if (G==0 | early==1)
quietly count if firm_tag==1
scalar eligible_firms = r(N)
drop firm_tag

quietly csdid grantedapp_norm ///
    ln1p_cum_funding_l1 cum_funding_rounds_l1 ///
    i.region_fe i.industry_fe if (G==0 | early==1), ///
    ivar(full_firm_id) time(year) gvar(G) method(dripw)

csdid_estat simple

* Event-study estimates followed immediately by their graph.
csdid_estat event, window(-4 4)
csdid_plot, yline(0, lcolor(gs8)) xline(0, lpattern(dash)) ///
    xtitle("Years relative to first VD") ///
    ytitle("ATT on normalized granted applications") ///
    title("(4) Early stage") ///
    graphregion(color(white)) name(Event_Early, replace)

csdid_estat group
display as text "Observations (complete-case input): " as result %12.0fc eligible_observations
display as text "Firms (complete-case input):        " as result %12.0fc eligible_firms
display as text "Control group: Never-treated"

********************************************************************************
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

csdid_estat group
display as text "Observations (complete-case input): " as result %12.0fc eligible_observations
display as text "Firms (complete-case input):        " as result %12.0fc eligible_firms
display as text "Control group: Never-treated"

log close
