version 19
clear all
set more off
set linesize 255
capture log close _all

global R "C:/Users/user/Documents/VD/outputs/csdid_historical_replication_verified"
global D "$R/MASTER_CS_TABLE_restored.dta"

log using "$R/MASTER_replicate_Table1_Figure1.log", replace text
graph set window fontface "Times New Roman"
graph set print fontface "Times New Roman"

********************************************************************************
* PURPOSE
* Restore Table 1 and Figure 1 from the verified 88,547-row historical panel.
* DV is the RAW firm-year count of applications ultimately granted by 2024.
* Never-treated firms are controls. Treatment year is the first VD year.
********************************************************************************

use "$D", clear
isid full_firm_id year
assert _N == 88547
quietly levelsof full_firm_id, local(allfirms)
display as result "RESTORED PANEL: observations=" _N " firms=7273"

foreach v in ln1p_cum_funding_l1 cum_funding_rounds_l1 region_fe industry_fe {
    replace `v' = 0 if missing(`v')
}
xtset full_firm_id year

********************************************************************************
* TABLE 1: five columns. Run DRIPW (Claude replication) and REG (old Stata check).
********************************************************************************
capture program drop run_cs
program define run_cs
    syntax, Label(string) [Condition(string)] Method(string)
    preserve
        if `"`condition'"' != "" keep if `condition'
        display as text _newline "=== TABLE1_BEGIN label=`label' method=`method' ==="
        quietly count
        display as result "OBS=" r(N)
        quietly egen __tag = tag(full_firm_id)
        quietly count if __tag
        display as result "FIRMS=" r(N)
        drop __tag

        csdid apps_ult_granted ln1p_cum_funding_l1 cum_funding_rounds_l1 ///
            i.region_fe i.industry_fe, ivar(full_firm_id) time(year) ///
            gvar(g_first_vd) method(`method')
        csdid_estat simple
        estimates store simple_`label'_`method'
        csdid_estat event, window(-4 4)
        estimates store event_`label'_`method'
        display as text "=== TABLE1_END label=`label' method=`method' ==="
    restore
end

foreach m in dripw {
    run_cs, label(all) method(`m')
    * Subgroup restriction applies to treated firms; all never-treated controls remain.
    run_cs, label(noprior) condition("g_first_vd==0 | prior_patent_vd==0") method(`m')
    run_cs, label(prior) condition("g_first_vd==0 | prior_patent_vd==1") method(`m')
    run_cs, label(early) condition("g_first_vd==0 | early_stage_vd==1") method(`m')
    run_cs, label(late) condition("g_first_vd==0 | early_stage_vd==0") method(`m')
}

********************************************************************************
* FIGURE 1A: cohort-aligned raw means, weighted by treated cohort-cell N.
********************************************************************************
tempfile cells
tempname h
postfile `h' int cohort byte event_time str8 group double mean_y long wt using `cells', replace
levelsof g_first_vd if g_first_vd>0, local(cohorts)
foreach g of local cohorts {
    forvalues k=-4/4 {
        local y=`g'+`k'
        quietly count if g_first_vd==`g' & year==`y'
        local n=r(N)
        if `n'>0 {
            quietly summarize apps_ult_granted if g_first_vd==`g' & year==`y', meanonly
            local mt=r(mean)
            quietly summarize apps_ult_granted if g_first_vd==0 & year==`y', meanonly
            if r(N)>0 {
                post `h' (`g') (`k') ("Treated") (`mt') (`n')
                post `h' (`g') (`k') ("Control") (r(mean)) (`n')
            }
        }
    }
}
postclose `h'
use `cells', clear
collapse (mean) mean_y [aw=wt], by(event_time group)
sort group event_time
export delimited using "$R/Figure1A_raw_means.csv", replace

twoway ///
 (connected mean_y event_time if group=="Treated", sort msymbol(O) lcolor(maroon) mcolor(maroon)) ///
 (connected mean_y event_time if group=="Control", sort msymbol(S) lcolor(navy) mcolor(navy)), ///
 xline(-0.5, lpattern(dash) lcolor(gs8)) ///
 xtitle("Event time (t - G)") ytitle("Applications per firm-year") ///
 title("Raw cohort-aligned means: ultimately granted applications") ///
 legend(order(1 "VD-backed (treated)" 2 "Never VD (control)")) ///
 graphregion(color(white)) name(Figure1A_restored, replace)
graph export "$R/Figure1A_restored.png", replace width(2400)
graph save "$R/Figure1A_restored.gph", replace

********************************************************************************
* FIGURE 1B: DRIPW Callaway-Sant'Anna event study.
********************************************************************************
estimates restore event_all_dripw
csdid_plot, group(0) ///
    title("Callaway-Sant'Anna event study: ultimately granted applications") ///
    xtitle("Event time (t - G)") ytitle("ATT on raw application count") ///
    graphregion(color(white)) name(Figure1B_restored, replace)
graph export "$R/Figure1B_restored.png", replace width(2400)
graph save "$R/Figure1B_restored.gph", replace

log close
exit, clear
