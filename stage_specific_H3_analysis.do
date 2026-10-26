clear all
set more off
capture log close
log using "C:/Users/user/Documents/VD/stage_specific_H3_output.log", replace text

tempfile stage_xwalk
import delimited using "C:/Users/user/Documents/VD/.artifact_work/stage_crosswalk.csv", varnames(1) encoding(UTF-8) clear
keep firm_id stage4 stage_label max_series_at_reference reference_year cutoff_date formal_rounds_by_reference stage_inference_method
isid firm_id
save `stage_xwalk'

use "C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms/260122 winsorization.dta", clear
merge 1:1 firm_id using `stage_xwalk'
assert _merge==3
drop _merge

label define stage4lbl 0 "Unclassified" 1 "Seed" 2 "Series A" 3 "Series B" 4 "Series C+", replace
label values stage4 stage4lbl
label variable stage4 "Funding stage at VD or pseudo-treatment reference point"

compress
save "C:/Users/user/Documents/VD/260122 winsorization_stage4.dta", replace

display "Matched sample and stage distribution"
count
tab stage4 VD, row col missing

capture file close results
file open results using "C:/Users/user/Documents/VD/stage_specific_H3_results.csv", write replace text
file write results "model,stage,stage_code,effect,se,p_value,ci_low,ci_high,n,df_r" _n

* Model 1: preferred common-slope interaction model matching the draft H3 specification.
reg ln_patentbyfiling_win3 i.VD##ib1.stage4 patentdummybyfiling ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2 if inrange(stage4,1,4)
estimates store stage_interaction
testparm 1.VD#2.stage4 1.VD#3.stage4 1.VD#4.stage4
scalar joint_p = r(p)
margins stage4, dydx(VD) post
matrix b = e(b)
matrix V = e(V)
scalar df = e(df_r)
scalar nmodel = e(N)
forvalues j=1/4 {
    local k = `j' + 4
    scalar eff = b[1,`k']
    scalar se = sqrt(V[`k',`k'])
    scalar pv = 2*ttail(df,abs(eff/se))
    scalar lo = eff-invttail(df,.025)*se
    scalar hi = eff+invttail(df,.025)*se
    local slabel : label stage4lbl `j'
    file write results "interaction_margins,`slabel',`j'," %12.8f (eff) "," %12.8f (se) "," %12.8f (pv) "," %12.8f (lo) "," %12.8f (hi) "," %9.0f (nmodel) "," %9.0f (df) _n
}

* Model 2: fully saturated with the prior-patent moderation used in draft Column 4.
reg ln_patentbyfiling_win3 i.VD##ib1.stage4 i.VD##ib0.patentdummybyfiling ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2 if inrange(stage4,1,4)
estimates store stage_interaction_full
margins stage4, dydx(VD) post
matrix b = e(b)
matrix V = e(V)
scalar df = e(df_r)
scalar nmodel = e(N)
forvalues j=1/4 {
    local k = `j' + 4
    scalar eff = b[1,`k']
    scalar se = sqrt(V[`k',`k'])
    scalar pv = 2*ttail(df,abs(eff/se))
    scalar lo = eff-invttail(df,.025)*se
    scalar hi = eff+invttail(df,.025)*se
    local slabel : label stage4lbl `j'
    file write results "interaction_full_margins,`slabel',`j'," %12.8f (eff) "," %12.8f (se) "," %12.8f (pv) "," %12.8f (lo) "," %12.8f (hi) "," %9.0f (nmodel) "," %9.0f (df) _n
}

* Model 3: separate regressions by stage, allowing control slopes to vary.
forvalues j=1/4 {
    quietly reg ln_patentbyfiling_win3 VD patentdummybyfiling ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2 if stage4==`j'
    scalar eff = _b[VD]
    scalar se = _se[VD]
    scalar df = e(df_r)
    scalar pv = 2*ttail(df,abs(eff/se))
    scalar lo = eff-invttail(df,.025)*se
    scalar hi = eff+invttail(df,.025)*se
    scalar nmodel = e(N)
    local slabel : label stage4lbl `j'
    file write results "separate_stage_regression,`slabel',`j'," %12.8f (eff) "," %12.8f (se) "," %12.8f (pv) "," %12.8f (lo) "," %12.8f (hi) "," %9.0f (nmodel) "," %9.0f (df) _n
}

file close results

display "Joint test p-value for VD-by-stage interactions = " %9.6f joint_p
estimates restore stage_interaction
reg ln_patentbyfiling_win3 i.VD##ib1.stage4 patentdummybyfiling ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2 if inrange(stage4,1,4), vce(robust)
margins stage4, dydx(VD)

log close
exit, clear
