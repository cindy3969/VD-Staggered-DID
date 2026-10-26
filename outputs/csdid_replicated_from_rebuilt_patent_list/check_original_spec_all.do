version 19
clear all
set more off
capture log close _all
global R "C:/Users/user/Documents/VD/outputs/csdid_replicated_from_rebuilt_patent_list"
log using "$R/check_original_spec_all.log", replace text
use "$R/csdid_rebuilt_patent_panel.dta", clear
drop if g_first_vd > 0 & g_first_vd <= founding_year
sort full_firm_id year
by full_firm_id: gen early_stage_l1 = early_stage[_n-1]
replace prior_patent_l1 = 0 if missing(prior_patent_l1)
replace early_stage_l1 = 1 if missing(early_stage_l1)
replace ln1p_cum_funding_l1 = 0 if missing(ln1p_cum_funding_l1)
replace cum_funding_rounds_l1 = 0 if missing(cum_funding_rounds_l1)
replace region_fe = 0 if missing(region_fe)
replace industry_fe = 0 if missing(industry_fe)
xtset full_firm_id year
csdid apps_ult_granted prior_patent_l1 early_stage_l1 ln1p_cum_funding_l1 ///
    cum_funding_rounds_l1 founding_year i.region_fe i.industry_fe, ///
    ivar(full_firm_id) time(year) gvar(g_first_vd) method(reg)
csdid_estat simple
csdid_estat event, window(-4 4)
log close
exit, clear
