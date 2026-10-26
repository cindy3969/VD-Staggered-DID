version 19
clear all
set more off
set linesize 255
capture log close _all
log using "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected/MASTER_csdid_all_applications.log", replace text

* Table 11: Callaway-Sant'Anna DRIPW. DV: grantedapp_norm (NOT log).
* Prior-patent subgroup and covariates retained; stage groups now use late at G-1.
* Read/filter once. Each model uses an if condition without deleting subgroups.
* Counts describe complete-case input; individual ATT(g,t) samples can differ.
* Figures 1-3 are displayed and saved as PNG/GPH. No datasets are saved.
* To run Table 11 and Figures 1-3 only, select from the top through log close.
* The pre-existing citation-quality section below log close is retained.

* Fixed PRE-treatment stage: latest observed equity stage through G-1.
* late=1: explicit Series C or above; late=0: Seed/Angel/Series A/B.
* Unknown/non-Series categories remain missing, NOT zero.
capture program drop construct_late
program define construct_late
    confirm variable full_firm_id year G stage_preyear_text
    capture drop late
    capture drop late_at_G
    capture drop stage_at_G
    gen str244 stage_at_G = lower(strtrim(stage_preyear_text)) if G>0 & year==G
    gen byte late_at_G = .
    replace late_at_G = 1 if G>0 & year==G & regexm(stage_at_G,"^series [c-z][0-9]*$")
    replace late_at_G = 0 if G>0 & year==G & ///
        (regexm(stage_at_G,"^series [ab][0-9]*$") | inlist(stage_at_G,"seed","pre-seed","angel"))
    bysort full_firm_id: egen byte late = max(late_at_G)
    label variable late "Series C+ through G-1 (1); Seed through B (0); unknown missing"
    label define late_stage_label 0 "Seed through Series B" 1 "Series C+", replace
    label values late late_stage_label
    drop late_at_G stage_at_G
end

frame change default
use "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected/firm_year_all_applications_and_truncation_specs.dta", clear
construct_late
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

* Keep the aggregated event estimates, not the underlying ATT(g,t) matrix.
matrix fig_all_b = r(b)
matrix fig_all_V = r(V)

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

* Keep the aggregated event estimates, not the underlying ATT(g,t) matrix.
matrix fig_noprior_b = r(b)
matrix fig_noprior_V = r(V)

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

* Keep the aggregated event estimates, not the underlying ATT(g,t) matrix.
matrix fig_prior_b = r(b)
matrix fig_prior_V = r(V)

csdid_estat group
display as text "Observations (complete-case input): " as result %12.0fc eligible_observations
display as text "Firms (complete-case input):        " as result %12.0fc eligible_firms
display as text "Control group: Never-treated"

********************************************************************************
* (4) Seed through Series B
********************************************************************************
display as result "(4) Seed through Series B"
quietly count if (G==0 | late==0)
scalar eligible_observations = r(N)
egen byte firm_tag = tag(full_firm_id) if (G==0 | late==0)
quietly count if firm_tag==1
scalar eligible_firms = r(N)
drop firm_tag

quietly csdid grantedapp_norm ///
    ln1p_cum_funding_l1 cum_funding_rounds_l1 ///
    i.region_fe i.industry_fe if (G==0 | late==0), ///
    ivar(full_firm_id) time(year) gvar(G) method(dripw)

csdid_estat simple

* Event-study estimates followed immediately by their graph.
csdid_estat event, window(-4 4)
csdid_plot, yline(0, lcolor(gs8)) xline(0, lpattern(dash)) ///
    xtitle("Years relative to first VD") ///
    ytitle("ATT on normalized granted applications") ///
    title("(4) Seed through Series B") ///
    graphregion(color(white)) name(Event_NonLate, replace)

* Keep the aggregated event estimates, not the underlying ATT(g,t) matrix.
matrix fig_nonlate_b = r(b)
matrix fig_nonlate_V = r(V)

csdid_estat group
display as text "Observations (complete-case input): " as result %12.0fc eligible_observations
display as text "Firms (complete-case input):        " as result %12.0fc eligible_firms
display as text "Control group: Never-treated"

********************************************************************************
* (5) Series C+
********************************************************************************
display as result "(5) Series C+"
quietly count if (G==0 | late==1)
scalar eligible_observations = r(N)
egen byte firm_tag = tag(full_firm_id) if (G==0 | late==1)
quietly count if firm_tag==1
scalar eligible_firms = r(N)
drop firm_tag

quietly csdid grantedapp_norm ///
    ln1p_cum_funding_l1 cum_funding_rounds_l1 ///
    i.region_fe i.industry_fe if (G==0 | late==1), ///
    ivar(full_firm_id) time(year) gvar(G) method(dripw)

csdid_estat simple

* Event-study estimates followed immediately by their graph.
csdid_estat event, window(-4 4)
csdid_plot, yline(0, lcolor(gs8)) xline(0, lpattern(dash)) ///
    xtitle("Years relative to first VD") ///
    ytitle("ATT on normalized granted applications") ///
    title("(5) Series C+") ///
    graphregion(color(white)) name(Event_Late, replace)

* Keep the aggregated event estimates, not the underlying ATT(g,t) matrix.
matrix fig_late_b = r(b)
matrix fig_late_V = r(V)

csdid_estat group
display as text "Observations (complete-case input): " as result %12.0fc eligible_observations
display as text "Firms (complete-case input):        " as result %12.0fc eligible_firms
display as text "Control group: Never-treated"


********************************************************************************
* FIGURES 1-3: CURRENT grantedapp_norm, not historical hard-coded coefficients.
* grantedapp_norm is used as supplied; no new truncation adjustment is made here.
* Run this file from the top so that the five fig_* matrices exist.
* Only PNG/GPH graphs are saved; the source DTA is NEVER overwritten.
* Figure 1/2: same C&S estimates as Table 11, including nonzero pre-period ATTs.
* Figure 3: separate TWFE, Sun-Abraham and unweighted stacked regressions.
* These estimators need not have identical weights, samples, or coefficients.
* C&S and Sun-Abraham/stacked specify never-treated controls. Conventional TWFE
* can also implicitly compare already-treated cohorts; do not label it as
* using exclusively never-treated comparisons.
********************************************************************************
graph set window fontface "Times New Roman"
graph set print fontface "Times New Roman"

* Nine event times, with coefficient names matched explicitly.
frame create figure_events
frame change figure_events
set obs 9
generate int event_time = _n-5
generate str4 cs_term = cond(event_time<0, "Tm"+string(abs(event_time)), "Tp"+string(event_time))

generate double att_all = el(fig_all_b,1,colnumb(fig_all_b,cs_term))
generate double se_all = sqrt(el(fig_all_V,colnumb(fig_all_b,cs_term),colnumb(fig_all_b,cs_term)))
assert !missing(att_all,se_all)
generate double lo_all = att_all-invnormal(.975)*se_all
generate double hi_all = att_all+invnormal(.975)*se_all

generate double att_noprior = el(fig_noprior_b,1,colnumb(fig_noprior_b,cs_term))
generate double se_noprior = sqrt(el(fig_noprior_V,colnumb(fig_noprior_b,cs_term),colnumb(fig_noprior_b,cs_term)))
assert !missing(att_noprior,se_noprior)
generate double lo_noprior = att_noprior-invnormal(.975)*se_noprior
generate double hi_noprior = att_noprior+invnormal(.975)*se_noprior

generate double att_prior = el(fig_prior_b,1,colnumb(fig_prior_b,cs_term))
generate double se_prior = sqrt(el(fig_prior_V,colnumb(fig_prior_b,cs_term),colnumb(fig_prior_b,cs_term)))
assert !missing(att_prior,se_prior)
generate double lo_prior = att_prior-invnormal(.975)*se_prior
generate double hi_prior = att_prior+invnormal(.975)*se_prior

generate double att_nonlate = el(fig_nonlate_b,1,colnumb(fig_nonlate_b,cs_term))
generate double se_nonlate = sqrt(el(fig_nonlate_V,colnumb(fig_nonlate_b,cs_term),colnumb(fig_nonlate_b,cs_term)))
assert !missing(att_nonlate,se_nonlate)
generate double lo_nonlate = att_nonlate-invnormal(.975)*se_nonlate
generate double hi_nonlate = att_nonlate+invnormal(.975)*se_nonlate

generate double att_late = el(fig_late_b,1,colnumb(fig_late_b,cs_term))
generate double se_late = sqrt(el(fig_late_V,colnumb(fig_late_b,cs_term),colnumb(fig_late_b,cs_term)))
assert !missing(att_late,se_late)
generate double lo_late = att_late-invnormal(.975)*se_late
generate double hi_late = att_late+invnormal(.975)*se_late

* Figure 1B. Pointwise 95% confidence intervals from csdid.
twoway (rcap lo_all hi_all event_time, lcolor(navy)) ///
    (connected att_all event_time, lcolor(navy) mcolor(black) msymbol(O)), ///
    xlabel(-4(1)4) xline(0,lpattern(dash) lcolor(gs8)) yline(0,lcolor(gs8)) ///
    xtitle("Years relative to first VD") ytitle("ATT on normalized granted applications") ///
    title("(b) Callaway-Sant'Anna event study", size(medsmall)) legend(off) ///
    graphregion(color(white)) name(Figure1B,replace)

* Figure 2. Offset points so that the two confidence intervals remain visible.
generate double event_left = event_time-.07
generate double event_right = event_time+.07
twoway (rcap lo_noprior hi_noprior event_left, lcolor(navy)) ///
    (scatter att_noprior event_left, mcolor(navy) msymbol(D)) ///
    (rcap lo_prior hi_prior event_right, lcolor(maroon)) ///
    (scatter att_prior event_right, mcolor(maroon) msymbol(T)), ///
    xlabel(-4(1)4) xline(-.5,lpattern(dash) lcolor(gs8)) yline(0,lcolor(gs8)) ///
    xtitle("Years relative to first VD") ytitle("ATT on normalized granted applications") ///
    title("(a) By prior technological assets", size(medsmall)) ///
    legend(order(2 "No prior patent" 4 "Prior patent") rows(1) position(6) size(small)) ///
    graphregion(color(white)) name(Figure2A,replace)
twoway (rcap lo_nonlate hi_nonlate event_left, lcolor(maroon)) ///
    (scatter att_nonlate event_left, mcolor(maroon) msymbol(T)) ///
    (rcap lo_late hi_late event_right, lcolor(navy)) ///
    (scatter att_late event_right, mcolor(navy) msymbol(D)), ///
    xlabel(-4(1)4) xline(-.5,lpattern(dash) lcolor(gs8)) yline(0,lcolor(gs8)) ///
    xtitle("Years relative to first VD") ytitle("ATT on normalized granted applications") ///
    title("(b) By funding stage", size(medsmall)) ///
    legend(order(2 "Seed through Series B" 4 "Series C+") rows(1) position(6) size(small)) ///
    graphregion(color(white)) name(Figure2B,replace)
graph combine Figure2A Figure2B, cols(2) ///
    title("Figure 2. Heterogeneous event-study estimates", size(medium)) xsize(12) ysize(5) ///
    note("All never-treated controls retained in each subgroup. C&S pre-period estimates are not forced to zero at -1.", size(vsmall)) ///
    graphregion(color(white)) name(Figure2,replace)
graph export "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected/Figure2_grantedapp_norm.png", replace width(3600)
graph save "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected/Figure2_grantedapp_norm.gph", replace
frame change default

* Figure 1A. Never-treated means aligned to treated firms' calendar years.
* No pseudo-VD dates are assigned to the never-treated firms in C&S.
* Use the Table 11 complete-case input. Changing composition is allowed.
frame put year grantedapp_norm if G==0, into(figure_control)
frame figure_control: collapse (mean) control_mean=grantedapp_norm, by(year)
frame put full_firm_id year G grantedapp_norm if G>0, into(figure_means)
frame change figure_means
generate int event_time = year-G
keep if inrange(event_time,-4,4)
frlink m:1 year, frame(figure_control)
frget control_mean, from(figure_control)
assert !missing(control_mean)
collapse (mean) treated_mean=grantedapp_norm control_mean, by(event_time)
frlink 1:1 event_time, frame(figure_events)
frget att_all, from(figure_events)
* Illustration only: raw treated mean minus adjusted ATT does not necessarily
* equal a consistently reweighted causal counterfactual outcome level.
generate double counterfactual = treated_mean-att_all if event_time>=0
replace counterfactual = treated_mean if event_time==-1
generate str30 att_label = "ATT(t=3) = "+string(att_all,"%6.3f") if event_time==3
generate double label_y = (treated_mean+counterfactual)/2 if event_time==3
twoway (connected treated_mean event_time, lcolor(cranberry) mcolor(cranberry) msymbol(O)) ///
    (connected control_mean event_time, lcolor(navy) mcolor(navy) msymbol(S)) ///
    (line counterfactual event_time, lcolor(cranberry) lpattern(dash)) ///
    (rspike treated_mean counterfactual event_time if event_time==3, lcolor(cranberry)) ///
    (scatter label_y event_time if event_time==3, msymbol(none) mlabel(att_label) mlabpos(9) mlabcolor(black)), ///
    xlabel(-4(1)4) xline(0,lpattern(dash) lcolor(gs8)) ///
    xtitle("Years relative to first VD") ytitle("Mean normalized granted applications") ///
    title("(a) Observed means and illustrative counterfactual", size(medsmall)) ///
    legend(order(1 "VD-backed" 2 "Never-treated" 3 "Treated mean minus ATT") rows(2) position(6) size(small)) ///
    graphregion(color(white)) name(Figure1A,replace)
graph combine Figure1A Figure1B, cols(2) ///
    title("Figure 1. Diagnostic analysis for the staggered DiD design", size(medium)) xsize(12) ysize(5) ///
    graphregion(color(white)) name(Figure1,replace)
graph export "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected/Figure1_grantedapp_norm.png", replace width(3600)
graph save "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected/Figure1_grantedapp_norm.gph", replace
frame change default

********************************************************************************
* Figure 3. Alternative estimators. Baseline = -1; original-firm clustered SE.
* Requires installed reghdfe and eventstudyinteract (already on this computer).
* Sun-Abraham command documentation: https://github.com/lsun20/EventStudyInteract
* IW coefficients/covariance are e(b_iw)/e(V_iw), NOT e(b)/e(V).
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
display as result "Figure 1-3 completed. PNG and editable GPH are in csdid_all_applications_corrected."
* No save command: the existing panel DTA remains unchanged.


log close

********************************************************************************
* Added 2026-10-19: annual patent quality, v1-v4, levels (NO log, NO win3).
* One firm-year outcome averages corrected application citation quality over
* ultimately granted applications FILED in that year. Citation cutoff: 2024.
* v1: sum of filing-year x citation-year normalized annual citations.
* v2: v1 with primary CPC3 added to the normalization cells.
* v3: cumulative citations / post-grant exposure, filing-cohort normalized.
* v4: cumulative citations / filing-year x CPC3 mean cumulative citations.
* No eligible patents => missing, as in original cross-sectional v1-v4.
* Table 11: five samples, never-treated controls, simple and event aggregates.
* Table 12: full sample, never-treated vs not-yet-treated; event -4..4, group.
* Each block reloads the full panel: original grantedapp_norm filtering is NOT
* carried over. Original outcomes, covariates and subgroup flags are preserved.
* Corrected citing-patent grant dates are used; old citation_date was invalid.
********************************************************************************
********************************************************************************
* PATENT QUALITY v1: norm_cite_perpat_v1 (levels; no log)
* Table 11: five subgroups. Table 12: never-treated / not-yet-treated.
********************************************************************************
global P "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected"
global Q "$P/citation_quality_20261019"
capture log close _all
log using "$Q/quality_v1.log", text replace
use "$P/firm_year_all_applications_and_truncation_specs.dta", clear
construct_late
local dv norm_cite_perpat_v1
keep if year<=2024
drop if missing(`dv',ln1p_cum_funding_l1,cum_funding_rounds_l1,region_fe,industry_fe,full_firm_id,year,G)
tempname H
postfile `H' str12 sample str12 control str12 aggregation str40 effect double att se p N firms int rc using "$Q/quality_v1_results.dta", replace
foreach sample in all noprior prior nonlate late notyet {
    local condition "1"
    local opt ""
    local ctrl "never"
    if "`sample'"=="noprior" local condition "G==0 | prior==0"
    if "`sample'"=="prior" local condition "G==0 | prior==1"
    if "`sample'"=="nonlate" local condition "G==0 | late==0"
    if "`sample'"=="late" local condition "G==0 | late==1"
    if "`sample'"=="notyet" {
        local opt "notyet"
        local ctrl "notyet"
    }
    quietly count if `condition'
    local N=r(N)
    egen byte tag=tag(full_firm_id) if `condition'
    quietly count if tag==1
    local firms=r(N)
    drop tag
    display "BEGIN_SPEC v1 `sample' N=`N' firms=`firms'"
    capture quietly csdid `dv' ln1p_cum_funding_l1 cum_funding_rounds_l1 i.region_fe i.industry_fe if `condition', ivar(full_firm_id) time(year) gvar(G) method(dripw) `opt'
    local rc=_rc
    if `rc' {
        post `H' ("`sample'") ("`ctrl'") ("failed") ("csdid") (.) (.) (.) (`N') (`firms') (`rc')
        continue
    }
    foreach agg in simple event group {
        local window ""
        if "`agg'"=="event" local window ", window(-4 4)"
        capture noisily csdid_estat `agg' `window'
        local rc=_rc
        if `rc' {
            post `H' ("`sample'") ("`ctrl'") ("`agg'") ("failed") (.) (.) (.) (`N') (`firms') (`rc')
            continue
        }
        matrix T=r(table)
        local names: colnames T
        local j=0
        foreach term of local names {
            local ++j
            post `H' ("`sample'") ("`ctrl'") ("`agg'") ("`term'") (T[1,`j']) (T[2,`j']) (T[4,`j']) (`N') (`firms') (0)
        }
    }
    display "END_SPEC v1 `sample'"
}
postclose `H'
use "$Q/quality_v1_results.dta", clear
export delimited using "$Q/quality_v1_results.csv", replace
log close

********************************************************************************
* PATENT QUALITY v2: norm_cite_perpat_v2 (levels; no log)
* Table 11: five subgroups. Table 12: never-treated / not-yet-treated.
********************************************************************************
global P "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected"
global Q "$P/citation_quality_20261019"
capture log close _all
log using "$Q/quality_v2.log", text replace
use "$P/firm_year_all_applications_and_truncation_specs.dta", clear
construct_late
local dv norm_cite_perpat_v2
keep if year<=2024
drop if missing(`dv',ln1p_cum_funding_l1,cum_funding_rounds_l1,region_fe,industry_fe,full_firm_id,year,G)
tempname H
postfile `H' str12 sample str12 control str12 aggregation str40 effect double att se p N firms int rc using "$Q/quality_v2_results.dta", replace
foreach sample in all noprior prior nonlate late notyet {
    local condition "1"
    local opt ""
    local ctrl "never"
    if "`sample'"=="noprior" local condition "G==0 | prior==0"
    if "`sample'"=="prior" local condition "G==0 | prior==1"
    if "`sample'"=="nonlate" local condition "G==0 | late==0"
    if "`sample'"=="late" local condition "G==0 | late==1"
    if "`sample'"=="notyet" {
        local opt "notyet"
        local ctrl "notyet"
    }
    quietly count if `condition'
    local N=r(N)
    egen byte tag=tag(full_firm_id) if `condition'
    quietly count if tag==1
    local firms=r(N)
    drop tag
    display "BEGIN_SPEC v2 `sample' N=`N' firms=`firms'"
    capture quietly csdid `dv' ln1p_cum_funding_l1 cum_funding_rounds_l1 i.region_fe i.industry_fe if `condition', ivar(full_firm_id) time(year) gvar(G) method(dripw) `opt'
    local rc=_rc
    if `rc' {
        post `H' ("`sample'") ("`ctrl'") ("failed") ("csdid") (.) (.) (.) (`N') (`firms') (`rc')
        continue
    }
    foreach agg in simple event group {
        local window ""
        if "`agg'"=="event" local window ", window(-4 4)"
        capture noisily csdid_estat `agg' `window'
        local rc=_rc
        if `rc' {
            post `H' ("`sample'") ("`ctrl'") ("`agg'") ("failed") (.) (.) (.) (`N') (`firms') (`rc')
            continue
        }
        matrix T=r(table)
        local names: colnames T
        local j=0
        foreach term of local names {
            local ++j
            post `H' ("`sample'") ("`ctrl'") ("`agg'") ("`term'") (T[1,`j']) (T[2,`j']) (T[4,`j']) (`N') (`firms') (0)
        }
    }
    display "END_SPEC v2 `sample'"
}
postclose `H'
use "$Q/quality_v2_results.dta", clear
export delimited using "$Q/quality_v2_results.csv", replace
log close

********************************************************************************
* PATENT QUALITY v3: norm_cite_perpat_v3 (levels; no log)
* Table 11: five subgroups. Table 12: never-treated / not-yet-treated.
********************************************************************************
global P "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected"
global Q "$P/citation_quality_20261019"
capture log close _all
log using "$Q/quality_v3.log", text replace
use "$P/firm_year_all_applications_and_truncation_specs.dta", clear
construct_late
local dv norm_cite_perpat_v3
keep if year<=2024
drop if missing(`dv',ln1p_cum_funding_l1,cum_funding_rounds_l1,region_fe,industry_fe,full_firm_id,year,G)
tempname H
postfile `H' str12 sample str12 control str12 aggregation str40 effect double att se p N firms int rc using "$Q/quality_v3_results.dta", replace
foreach sample in all noprior prior nonlate late notyet {
    local condition "1"
    local opt ""
    local ctrl "never"
    if "`sample'"=="noprior" local condition "G==0 | prior==0"
    if "`sample'"=="prior" local condition "G==0 | prior==1"
    if "`sample'"=="nonlate" local condition "G==0 | late==0"
    if "`sample'"=="late" local condition "G==0 | late==1"
    if "`sample'"=="notyet" {
        local opt "notyet"
        local ctrl "notyet"
    }
    quietly count if `condition'
    local N=r(N)
    egen byte tag=tag(full_firm_id) if `condition'
    quietly count if tag==1
    local firms=r(N)
    drop tag
    display "BEGIN_SPEC v3 `sample' N=`N' firms=`firms'"
    capture quietly csdid `dv' ln1p_cum_funding_l1 cum_funding_rounds_l1 i.region_fe i.industry_fe if `condition', ivar(full_firm_id) time(year) gvar(G) method(dripw) `opt'
    local rc=_rc
    if `rc' {
        post `H' ("`sample'") ("`ctrl'") ("failed") ("csdid") (.) (.) (.) (`N') (`firms') (`rc')
        continue
    }
    foreach agg in simple event group {
        local window ""
        if "`agg'"=="event" local window ", window(-4 4)"
        capture noisily csdid_estat `agg' `window'
        local rc=_rc
        if `rc' {
            post `H' ("`sample'") ("`ctrl'") ("`agg'") ("failed") (.) (.) (.) (`N') (`firms') (`rc')
            continue
        }
        matrix T=r(table)
        local names: colnames T
        local j=0
        foreach term of local names {
            local ++j
            post `H' ("`sample'") ("`ctrl'") ("`agg'") ("`term'") (T[1,`j']) (T[2,`j']) (T[4,`j']) (`N') (`firms') (0)
        }
    }
    display "END_SPEC v3 `sample'"
}
postclose `H'
use "$Q/quality_v3_results.dta", clear
export delimited using "$Q/quality_v3_results.csv", replace
log close

********************************************************************************
* PATENT QUALITY v4: norm_cite_perpat_v4 (levels; no log)
* Table 11: five subgroups. Table 12: never-treated / not-yet-treated.
********************************************************************************
global P "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected"
global Q "$P/citation_quality_20261019"
capture log close _all
log using "$Q/quality_v4.log", text replace
use "$P/firm_year_all_applications_and_truncation_specs.dta", clear
construct_late
local dv norm_cite_perpat_v4
keep if year<=2024
drop if missing(`dv',ln1p_cum_funding_l1,cum_funding_rounds_l1,region_fe,industry_fe,full_firm_id,year,G)
tempname H
postfile `H' str12 sample str12 control str12 aggregation str40 effect double att se p N firms int rc using "$Q/quality_v4_results.dta", replace
foreach sample in all noprior prior nonlate late notyet {
    local condition "1"
    local opt ""
    local ctrl "never"
    if "`sample'"=="noprior" local condition "G==0 | prior==0"
    if "`sample'"=="prior" local condition "G==0 | prior==1"
    if "`sample'"=="nonlate" local condition "G==0 | late==0"
    if "`sample'"=="late" local condition "G==0 | late==1"
    if "`sample'"=="notyet" {
        local opt "notyet"
        local ctrl "notyet"
    }
    quietly count if `condition'
    local N=r(N)
    egen byte tag=tag(full_firm_id) if `condition'
    quietly count if tag==1
    local firms=r(N)
    drop tag
    display "BEGIN_SPEC v4 `sample' N=`N' firms=`firms'"
    capture quietly csdid `dv' ln1p_cum_funding_l1 cum_funding_rounds_l1 i.region_fe i.industry_fe if `condition', ivar(full_firm_id) time(year) gvar(G) method(dripw) `opt'
    local rc=_rc
    if `rc' {
        post `H' ("`sample'") ("`ctrl'") ("failed") ("csdid") (.) (.) (.) (`N') (`firms') (`rc')
        continue
    }
    foreach agg in simple event group {
        local window ""
        if "`agg'"=="event" local window ", window(-4 4)"
        capture noisily csdid_estat `agg' `window'
        local rc=_rc
        if `rc' {
            post `H' ("`sample'") ("`ctrl'") ("`agg'") ("failed") (.) (.) (.) (`N') (`firms') (`rc')
            continue
        }
        matrix T=r(table)
        local names: colnames T
        local j=0
        foreach term of local names {
            local ++j
            post `H' ("`sample'") ("`ctrl'") ("`agg'") ("`term'") (T[1,`j']) (T[2,`j']) (T[4,`j']) (`N') (`firms') (0)
        }
    }
    display "END_SPEC v4 `sample'"
}
postclose `H'
use "$Q/quality_v4_results.dta", clear
export delimited using "$Q/quality_v4_results.csv", replace
log close
