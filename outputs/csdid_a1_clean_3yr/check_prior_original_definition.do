version 19
clear all
set more off
set linesize 255
capture log close _all
global R "C:/Users/user/Documents/VD/outputs/csdid_a1_clean_3yr"
log using "$R/check_prior_original_definition.log", replace text
use "$R/csdid_A1_only_granted_within3y_panel.dta", clear
foreach v in ln1p_cum_funding_l1 cum_funding_rounds_l1 region_fe industry_fe {
    replace `v'=0 if missing(`v')
}
keep if G==0 | prior_original==1
xtset full_firm_id year
foreach y in granted_3yr_a1 granted_3yr_a1_title_dedup {
    display as text "=== ORIGINAL_PRIOR_BEGIN outcome=`y' ==="
    csdid `y' ln1p_cum_funding_l1 cum_funding_rounds_l1 ///
        i.region_fe i.industry_fe, ivar(full_firm_id) time(year) ///
        gvar(G) method(dripw)
    csdid_estat simple
    csdid_estat event, window(-4 4)
    display as text "=== ORIGINAL_PRIOR_END outcome=`y' ==="
}
log close
exit, clear
