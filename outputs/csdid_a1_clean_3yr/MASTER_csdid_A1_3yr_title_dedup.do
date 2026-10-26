version 19
clear all
set more off
set linesize 255
capture log close _all
global R "C:/Users/user/Documents/VD/outputs/csdid_a1_clean_3yr"
log using "$R/MASTER_csdid_A1_3yr_title_dedup.log", replace text

use "$R/csdid_A1_only_granted_within3y_panel.dta", clear
isid full_firm_id year
foreach v in ln1p_cum_funding_l1 cum_funding_rounds_l1 region_fe industry_fe {
    replace `v'=0 if missing(`v')
}
xtset full_firm_id year

capture program drop run_clean
program define run_clean
    syntax, Outcome(name) Label(string) [Condition(string)]
    preserve
        if `"`condition'"'!="" keep if `condition'
        display as text _newline "=== CLEAN_BEGIN outcome=`outcome' sample=`label' ==="
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
        display as text "=== CLEAN_END outcome=`outcome' sample=`label' ==="
    restore
end

foreach y in granted_3yr_a1 granted_3yr_a1_title_dedup {
    run_clean, outcome(`y') label(all)
    run_clean, outcome(`y') label(noprior) condition("G==0 | prior==0")
    run_clean, outcome(`y') label(prior) condition("G==0 | prior==1")
    run_clean, outcome(`y') label(early) condition("G==0 | early==1")
    run_clean, outcome(`y') label(late) condition("G==0 | early==0")
}

log close
exit, clear
