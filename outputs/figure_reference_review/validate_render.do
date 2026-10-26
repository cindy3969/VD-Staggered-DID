version 19
clear all
set more off
set linesize 255
log using "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected/Figure_render_validation.log", text replace
* Internal rendering QA only. Use MASTER for estimation at full precision.
* Event estimates/SE below are from the just-completed Stata validation logs.
* Only diagonal variances are needed for pointwise error bars; not for tests.
use "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected/firm_year_all_applications_and_truncation_specs.dta", clear
keep if year<=2024
drop if missing(grantedapp_norm, ln1p_cum_funding_l1, cum_funding_rounds_l1, region_fe, industry_fe, full_firm_id, year, G)
matrix fig_all_b = (-0.0447464,0.102398,0.0458955,0.0181581,0.0039588,-0.1005589,-0.2541276,-0.2796762,-0.3035273)
matrix colnames fig_all_b = Tm4 Tm3 Tm2 Tm1 Tp0 Tp1 Tp2 Tp3 Tp4
matrix fig_all_se = (0.0025054830030400003,0.005250002357610001,0.0037075190323600004,0.0034248947107600003,0.0036746874086399997,0.0034371485798399995,0.007154859064960001,0.011946183961959999,0.01892283613609)
matrix fig_all_V = diag(fig_all_se)
matrix fig_noprior_b = (-0.0636113,-0.0653266,-0.0560991,-0.0513652,0.0696313,-0.0033504,0.0055828,-0.0476469,-0.0255838)
matrix colnames fig_noprior_b = Tm4 Tm3 Tm2 Tm1 Tp0 Tp1 Tp2 Tp3 Tp4
matrix fig_noprior_se = (0.00011504922121000001,0.00011370809956,0.00011842010041000001,0.00014525311441,0.000964288809,0.0010922033522500001,0.0028336458240000003,0.00667136102656,0.011831630792890001)
matrix fig_noprior_V = diag(fig_noprior_se)
matrix fig_prior_b = (-0.0172669,0.3937756,0.235324,0.1674308,-0.1441321,-0.3150813,-0.8411938,-0.8159438,-1.002929)
matrix colnames fig_prior_b = Tm4 Tm3 Tm2 Tm1 Tp0 Tp1 Tp2 Tp3 Tp4
matrix fig_prior_se = (0.018041781808089997,0.04092249830761,0.03674881332004,0.03214253751556,0.036922621686760006,0.031214196965160004,0.05917742234881,0.08027685222489,0.12170399732099998)
matrix fig_prior_V = diag(fig_prior_se)
matrix fig_early_b = (-0.0274636,-0.0109845,0.0200489,0.0534406,-0.0105837,-0.0726389,-0.1754119,-0.1442364,-0.1366388)
matrix colnames fig_early_b = Tm4 Tm3 Tm2 Tm1 Tp0 Tp1 Tp2 Tp3 Tp4
matrix fig_early_se = (0.00282288190864,0.005767172175610001,0.0031180274244900002,0.005696279391690001,0.0037549197507600004,0.0039225670041600005,0.00934506956601,0.011428614882090002,0.021716620063360004)
matrix fig_early_V = diag(fig_early_se)
matrix fig_late_b = (-0.0695013,0.2423187,0.0776251,-0.057738,0.0184508,-0.1785198,-0.4383242,-0.6798373,-0.8161545)
matrix colnames fig_late_b = Tm4 Tm3 Tm2 Tm1 Tp0 Tp1 Tp2 Tp3 Tp4
matrix fig_late_se = (0.007994523626409998,0.01837296209961,0.01615743512161,0.00849724458025,0.01928007229729,0.016953576394810002,0.02944789849521,0.07328163015364,0.08057666991609)
matrix fig_late_V = diag(fig_late_se)
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

generate double att_early = el(fig_early_b,1,colnumb(fig_early_b,cs_term))
generate double se_early = sqrt(el(fig_early_V,colnumb(fig_early_b,cs_term),colnumb(fig_early_b,cs_term)))
assert !missing(att_early,se_early)
generate double lo_early = att_early-invnormal(.975)*se_early
generate double hi_early = att_early+invnormal(.975)*se_early

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
twoway (rcap lo_early hi_early event_left, lcolor(maroon)) ///
    (scatter att_early event_left, mcolor(maroon) msymbol(T)) ///
    (rcap lo_late hi_late event_right, lcolor(navy)) ///
    (scatter att_late event_right, mcolor(navy) msymbol(D)), ///
    xlabel(-4(1)4) xline(-.5,lpattern(dash) lcolor(gs8)) yline(0,lcolor(gs8)) ///
    xtitle("Years relative to first VD") ytitle("ATT on normalized granted applications") ///
    title("(b) By funding stage", size(medsmall)) ///
    legend(order(2 "Early stage" 4 "Late stage") rows(1) position(6) size(small)) ///
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

log close
exit, clear
