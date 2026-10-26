version 19.0
clear all
set more off
capture log close _all
args y
global R "C:/Users/user/Documents/VD/outputs/table2_forward_citation_year_methods_39249"
log using "$R/csdid_`y'.log", replace text

use "$R/firm_year_with_citations.dta", clear
drop if g_first_vd > 0 & g_first_vd <= founding_year
foreach v in ln1p_cum_funding_l1 cum_funding_rounds_l1 region_fe industry_fe {
    replace `v' = 0 if missing(`v')
}
xtset full_firm_id year

capture program drop run_fc_spec
program define run_fc_spec
    syntax varname, Label(string) Keepif(string)
    preserve
    quietly keep if `keepif'
    quietly count
    display "=== BEGIN_SPEC outcome=`varlist' sample=`label' OBS_RAW=" r(N) " ==="
    quietly egen __tag=tag(full_firm_id)
    quietly count if __tag
    display "FIRMS_RAW=" r(N)
    drop __tag
    csdid `varlist' ln1p_cum_funding_l1 cum_funding_rounds_l1 i.region_fe i.industry_fe, ///
        ivar(full_firm_id) time(year) gvar(g_first_vd) method(dripw)
    csdid_estat simple
    csdid_estat event, window(-4 4)
    display "=== END_SPEC outcome=`varlist' sample=`label' ==="
    restore
end

run_fc_spec `y', label(all) keepif("1")
run_fc_spec `y', label(noprior) keepif("g_first_vd==0 | prior_patent_vd==0")
run_fc_spec `y', label(prior) keepif("g_first_vd==0 | prior_patent_vd==1")
run_fc_spec `y', label(early) keepif("g_first_vd==0 | early_stage_vd==1")
run_fc_spec `y', label(late) keepif("g_first_vd==0 | early_stage_vd==0")

log close
exit, clear
