version 19.0
clear all
set more off
capture log close _all
global R "C:/Users/user/Documents/VD/outputs/csdid_replicated_from_rebuilt_patent_list"
log using "$R/replicate_table1_and_figures.log", replace text

use "$R/csdid_rebuilt_patent_panel.dta", clear
drop if g_first_vd > 0 & g_first_vd <= founding_year
replace prior_patent_l1 = 0 if missing(prior_patent_l1)
replace ln1p_cum_funding_l1 = 0 if missing(ln1p_cum_funding_l1)
replace cum_funding_rounds_l1 = 0 if missing(cum_funding_rounds_l1)
replace time_first_vc = 0 if missing(time_first_vc)
replace region_fe = 0 if missing(region_fe)
replace industry_fe = 0 if missing(industry_fe)
xtset full_firm_id year

local y apps_ult_granted
local x prior_patent_l1 ln1p_cum_funding_l1 cum_funding_rounds_l1 founding_year i.region_fe i.industry_fe

capture program drop run_spec
program define run_spec
    syntax, Label(string) Keepif(string)
    preserve
    quietly keep if `keepif'
    quietly count
    display "=== BEGIN_SPEC `label' OBS_RAW=" r(N) " ==="
    quietly egen __tag=tag(full_firm_id)
    quietly count if __tag
    display "FIRMS_RAW=" r(N)
    drop __tag
    csdid apps_ult_granted prior_patent_l1 ln1p_cum_funding_l1 cum_funding_rounds_l1 founding_year i.region_fe i.industry_fe, ///
        ivar(full_firm_id) time(year) gvar(g_first_vd) method(dripw) long2
    estat simple, estore(simple_`label')
    estat event, window(-4 4) estore(event_`label')
    display "=== END_SPEC `label' ==="
    restore
end

run_spec, label(all) keepif("1")
run_spec, label(noprior) keepif("g_first_vd==0 | prior_patent_G==0")
run_spec, label(prior) keepif("g_first_vd==0 | prior_patent_G==1")
run_spec, label(early) keepif("g_first_vd==0 | early_stage_G==1")
run_spec, label(late) keepif("g_first_vd==0 | early_stage_G==0")

* Figure 1b: adjusted event study for all firms, never-treated comparison.
estimates restore event_all
csdid_plot, group(0) name(FIG1B, replace) ///
    title("Dynamic ATT: ultimately granted patent applications") ///
    xtitle("Years relative to first venture debt") ytitle("ATT on annual granted applications") ///
    xline(-0.5, lpattern(dash) lcolor(gs8)) yline(0, lcolor(gs8))
graph export "$R/Figure_1b_dynamic_ATT.png", replace width(3000)
graph save "$R/Figure_1b_dynamic_ATT.gph", replace

log close
exit, clear
