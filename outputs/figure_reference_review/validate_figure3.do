version 19
clear all
set more off
set linesize 255
log using "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected/Figure3_validation.log", text replace
use "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected/firm_year_all_applications_and_truncation_specs.dta", clear
keep if year<=2024
drop if missing(grantedapp_norm, ln1p_cum_funding_l1, cum_funding_rounds_l1, region_fe, industry_fe, full_firm_id, year, G)
frame create figure_events
frame figure_events: set obs 9
frame figure_events: generate int event_time=_n-5
graph set window fontface "Times New Roman"
graph set print fontface "Times New Roman"
********************************************************************************
* Figure 3. Alternative estimators. Baseline = -1; original-firm clustered SE.
* Requires installed reghdfe and eventstudyinteract (already on this computer).
* Region/industry are time invariant and absorbed by firm fixed effects.
* Tail indicators prevent all periods outside -4..4 becoming the reference.
* The <=-5 and >=5 tail bins impose common within-bin effects.
********************************************************************************
which reghdfe
which eventstudyinteract
generate int figure_event_time = year-G if G>0
generate byte figure_never = (G==0)
generate int figure_cohort = G if G>0
generate byte event_before = (figure_event_time<=-5 & G>0)
generate byte event_after = (figure_event_time>=5 & figure_event_time<. & G>0)
generate byte event_m4 = (figure_event_time==-4 & G>0)
generate byte event_m3 = (figure_event_time==-3 & G>0)
generate byte event_m2 = (figure_event_time==-2 & G>0)
generate byte event_p0 = (figure_event_time==0 & G>0)
generate byte event_p1 = (figure_event_time==1 & G>0)
generate byte event_p2 = (figure_event_time==2 & G>0)
generate byte event_p3 = (figure_event_time==3 & G>0)
generate byte event_p4 = (figure_event_time==4 & G>0)

display as result "Figure 3: original TWFE"
reghdfe grantedapp_norm event_m4 event_m3 event_m2 event_p0 event_p1 event_p2 event_p3 event_p4 ///
    event_before event_after ln1p_cum_funding_l1 cum_funding_rounds_l1, ///
    absorb(full_firm_id year) vce(cluster full_firm_id)
matrix figure_twfe_b = e(b)
matrix figure_twfe_V = e(V)
scalar figure_twfe_critical = invttail(e(df_r),.025)
test event_m4 event_m3 event_m2
scalar figure_twfe_pretrend_p = r(p)
display as text "TWFE joint pretrend p (-4,-3,-2; not tail bin): " as result figure_twfe_pretrend_p

display as result "Figure 3: Sun-Abraham interaction-weighted estimator"
eventstudyinteract grantedapp_norm event_m4 event_m3 event_m2 event_p0 event_p1 event_p2 event_p3 event_p4 ///
    event_before event_after, ///
    cohort(figure_cohort) control_cohort(figure_never) ///
    covariates(ln1p_cum_funding_l1 cum_funding_rounds_l1) ///
    absorb(full_firm_id year) vce(cluster full_firm_id)
matrix figure_sa_b = e(b_iw)
matrix figure_sa_V = e(V_iw)
scalar figure_sa_critical = invnormal(.975)

* Build cohort-specific stacks entirely in memory. Each stack contains only
* its treated cohort and never-treated firms in calendar years G-4..G+4.
* Unweighted conventional stacked regression: not the same C&S estimand.
* Cluster original firms across stacks, because controls recur across stacks.
frame put G if G>0, into(figure_cohorts)
frame change figure_cohorts
duplicates drop G, force
sort G
rename G stack_G
generate int stack_index = _n
scalar figure_number_cohorts = _N
frame change default
frame put full_firm_id year G grantedapp_norm ln1p_cum_funding_l1 cum_funding_rounds_l1 ///
    event_m4 event_m3 event_m2 event_p0 event_p1 event_p2 event_p3 event_p4, into(figure_stack)
frame change figure_stack
expand figure_number_cohorts
bysort full_firm_id year: generate int stack_index = _n
frlink m:1 stack_index, frame(figure_cohorts)
frget stack_G, from(figure_cohorts)
keep if (G==0 | G==stack_G) & inrange(year-stack_G,-4,4)
* Drop firm-stack units lacking the baseline outcome; never fill absent years.
bysort stack_index full_firm_id: egen byte has_baseline = max(year==stack_G-1)
keep if has_baseline==1
display as result "Figure 3: conventional unweighted stacked event study"
reghdfe grantedapp_norm event_m4 event_m3 event_m2 event_p0 event_p1 event_p2 event_p3 event_p4 ///
    i.stack_index#c.ln1p_cum_funding_l1 i.stack_index#c.cum_funding_rounds_l1, ///
    absorb(full_firm_id#stack_index year#stack_index) vce(cluster full_firm_id)
matrix figure_stack_b = e(b)
matrix figure_stack_V = e(V)
scalar figure_stack_critical = invttail(e(df_r),.025)
frame change figure_events
generate str12 regression_term = cond(event_time<0,"event_m"+string(abs(event_time)),"event_p"+string(event_time))

generate double b_twfe = el(figure_twfe_b,1,colnumb(figure_twfe_b,regression_term)) if event_time!=-1
generate double s_twfe = sqrt(el(figure_twfe_V,colnumb(figure_twfe_b,regression_term),colnumb(figure_twfe_b,regression_term))) if event_time!=-1
assert !missing(b_twfe,s_twfe) if event_time!=-1
replace b_twfe = 0 if event_time==-1
replace s_twfe = 0 if event_time==-1
generate double lower_twfe = b_twfe-figure_twfe_critical*s_twfe
generate double upper_twfe = b_twfe+figure_twfe_critical*s_twfe

generate double b_sa = el(figure_sa_b,1,colnumb(figure_sa_b,regression_term)) if event_time!=-1
generate double s_sa = sqrt(el(figure_sa_V,colnumb(figure_sa_b,regression_term),colnumb(figure_sa_b,regression_term))) if event_time!=-1
assert !missing(b_sa,s_sa) if event_time!=-1
replace b_sa = 0 if event_time==-1
replace s_sa = 0 if event_time==-1
generate double lower_sa = b_sa-figure_sa_critical*s_sa
generate double upper_sa = b_sa+figure_sa_critical*s_sa

generate double b_stack = el(figure_stack_b,1,colnumb(figure_stack_b,regression_term)) if event_time!=-1
generate double s_stack = sqrt(el(figure_stack_V,colnumb(figure_stack_b,regression_term),colnumb(figure_stack_b,regression_term))) if event_time!=-1
assert !missing(b_stack,s_stack) if event_time!=-1
replace b_stack = 0 if event_time==-1
replace s_stack = 0 if event_time==-1
generate double lower_stack = b_stack-figure_stack_critical*s_stack
generate double upper_stack = b_stack+figure_stack_critical*s_stack

generate double event_twfe = event_time-.10
generate double event_sa = event_time
generate double event_stack = event_time+.10
twoway (rcap lower_twfe upper_twfe event_twfe, lcolor(navy)) ///
    (scatter b_twfe event_twfe, mcolor(navy) msymbol(Dh)) ///
    (rcap lower_sa upper_sa event_sa, lcolor(maroon)) ///
    (scatter b_sa event_sa, mcolor(maroon) msymbol(Oh)) ///
    (rcap lower_stack upper_stack event_stack, lcolor(forest_green)) ///
    (scatter b_stack event_stack, mcolor(forest_green) msymbol(Th)), ///
    xlabel(-4(1)4) xline(-.5,lpattern(dash) lcolor(gs8)) yline(0,lcolor(gs8)) ///
    xtitle("Years relative to first VD") ytitle("Effect on normalized granted applications") ///
    title("Figure 3. Event studies across alternative estimators", size(medium)) ///
    legend(order(2 "Original TWFE" 4 "Sun and Abraham (2021)" 6 "Stacked") rows(1) position(6) size(small)) ///
    note("Reference: -1. Pointwise 95% CI. Firm-clustered SE. Stacked: unweighted.", size(vsmall)) ///
    graphregion(color(white)) xsize(9) ysize(5.5) name(Figure3,replace)
graph export "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected/Figure3_grantedapp_norm.png", replace width(3000)
graph save "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected/Figure3_grantedapp_norm.gph", replace
frame change default
display as result "Figure 3 validation completed."
* No save command: the existing panel DTA remains unchanged.

log close
exit, clear
