version 19.0
clear all
set more off
capture log close _all
global R "C:/Users/user/Documents/VD/outputs/csdid_historical_replication"
log using "$R/MASTER_replicate_historical_Table1_Figure1.log", replace text

use "$R/MASTER_CS_TABLE_rebuilt.dta", clear
keep if year<=2024
drop if g_first_vd>0 & g_first_vd<=founding_year
replace prior_granted_dummy_l1=0 if missing(prior_granted_dummy_l1)
replace early_stage_main_l1=1 if missing(early_stage_main_l1)
replace ln1p_cum_funding_l1=0 if missing(ln1p_cum_funding_l1)
replace cum_funding_rounds_l1=0 if missing(cum_funding_rounds_l1)
replace region_fe=0 if missing(region_fe)
replace industry_fe=0 if missing(industry_fe)
xtset full_firm_id year

capture program drop runone
program define runone
    syntax, Name(string) Condition(string)
    preserve
    keep if `condition'
    quietly count
    display "=== BEGIN `name' OBS=" r(N) " ==="
    egen __tag=tag(full_firm_id)
    quietly count if __tag
    display "FIRMS=" r(N)
    drop __tag
    csdid apps_ult_granted ///
        prior_granted_dummy_l1 early_stage_main_l1 ///
        ln1p_cum_funding_l1 cum_funding_rounds_l1 founding_year ///
        i.region_fe i.industry_fe, ///
        ivar(full_firm_id) time(year) gvar(g_first_vd) method(reg)
    estat simple, estore(simple_`name')
    estat event, window(-4 4) estore(event_`name')
    display "=== END `name' ==="
    restore
end

runone, name(all)     condition("1")
runone, name(noprior) condition("g_first_vd==0 | prior_patent_G==0")
runone, name(prior)   condition("g_first_vd==0 | prior_patent_G==1")
runone, name(early)   condition("g_first_vd==0 | early_stage_G==1")
runone, name(late)    condition("g_first_vd==0 | early_stage_G==0")

* Figure 1(a): cohort-aligned raw trajectories.
tempfile cells
tempname H
postfile `H' int cohort byte event_time str8 group double outcome_mean long cell_n using `cells', replace
levelsof g_first_vd if g_first_vd>0, local(gs)
foreach g of local gs {
    forvalues k=-4/4 {
        local yy=`g'+`k'
        quietly count if g_first_vd==`g' & year==`yy'
        local n=r(N)
        if `n'>0 {
            quietly summarize apps_ult_granted if g_first_vd==`g' & year==`yy', meanonly
            local mt=r(mean)
            quietly count if g_first_vd==0 & year==`yy'
            if r(N)>0 {
                quietly summarize apps_ult_granted if g_first_vd==0 & year==`yy', meanonly
                post `H' (`g') (`k') ("Treated") (`mt') (`n')
                post `H' (`g') (`k') ("Control") (r(mean)) (`n')
            }
        }
    }
}
postclose `H'
use `cells', clear
collapse (mean) outcome_mean [aw=cell_n], by(event_time group)
export delimited using "$R/Figure_1a_raw_data.csv", replace
twoway ///
 (connected outcome_mean event_time if group=="Treated", sort msymbol(O) lcolor(cranberry) mcolor(cranberry)) ///
 (connected outcome_mean event_time if group=="Control", sort msymbol(S) lcolor(navy) mcolor(navy)), ///
 xline(-.5,lpattern(dash) lcolor(gs8)) xlabel(-4(1)4) ///
 xtitle("Event time (t - G)") ytitle("Granted patent applications per firm-year") ///
 legend(order(1 "VD-backed (treated)" 2 "Never VD (control)")) ///
 title("Figure 1(a). Mean plots") graphregion(color(white)) name(FIG1A,replace)
graph export "$R/Figure_1a_raw_trajectories.png", replace width(3000)

estimates restore event_all
csdid_plot, group(0) name(FIG1B,replace) ///
 title("Figure 1(b). Dynamic ATT") ///
 xtitle("Years relative to first venture debt") ///
 ytitle("ATT on annual granted applications") ///
 xline(-.5,lpattern(dash) lcolor(gs8)) yline(0,lcolor(gs8))
graph export "$R/Figure_1b_dynamic_ATT.png", replace width(3000)
graph combine FIG1A FIG1B, cols(2) graphregion(color(white))
graph export "$R/Figure_1_combined.png", replace width(3600)
log close
