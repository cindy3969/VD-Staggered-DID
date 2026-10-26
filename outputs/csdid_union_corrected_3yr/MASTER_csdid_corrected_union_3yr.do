version 19
clear all
set more off
set linesize 255
capture log close _all
global R "C:/Users/user/Documents/VD/outputs/csdid_union_corrected_3yr"
log using "$R/MASTER_csdid_corrected_union_3yr.log", replace text
use "$R/firm_year_panel_corrected_3yr.dta", clear
foreach v in ln1p_cum_funding_l1 cum_funding_rounds_l1 region_fe industry_fe {
    replace `v'=0 if missing(`v')
}
xtset full_firm_id year
capture program drop run_u
program define run_u
    syntax, Outcome(name) Label(string) [Condition(string)]
    preserve
        if `"`condition'"'!="" keep if `condition'
        display as text _newline "=== UNION_BEGIN outcome=`outcome' sample=`label' ==="
        quietly count
        display as result "OBS=" r(N)
        quietly egen __tag=tag(full_firm_id)
        quietly count if __tag
        display as result "FIRMS=" r(N)
        drop __tag
        csdid `outcome' ln1p_cum_funding_l1 cum_funding_rounds_l1 ///
            i.region_fe i.industry_fe, ivar(full_firm_id) time(year) ///
            gvar(G) method(dripw)
        csdid_estat simple
        csdid_estat event, window(-4 4)
        display as text "=== UNION_END outcome=`outcome' sample=`label' ==="
    restore
end
foreach y in granted_3yr_corrected granted_3yr_title_dedup {
    run_u, outcome(`y') label(all)
    run_u, outcome(`y') label(noprior) condition("G==0 | prior==0")
    run_u, outcome(`y') label(prior) condition("G==0 | prior==1")
    run_u, outcome(`y') label(early) condition("G==0 | early==1")
    run_u, outcome(`y') label(late) condition("G==0 | early==0")
}
log close
exit, clear
