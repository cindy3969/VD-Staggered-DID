clear all
set more off
global ROOT "C:/Users/user/Documents/VD/outputs/psm_final_2820_package"
global OUT "$ROOT/table3_original2820_full_results"
use "$ROOT/table3_original_2820_cross_section_v2.dta", clear
capture drop priorpatentdummy_VD
gen priorpatentdummy_VD=1-patentdummybyfiling
capture drop ln_grantedbyfiling_norm_win3
gen ln_grantedbyfiling_norm_win3=ln(1+grantedpatentbyfiling_norm_win3)
* Table 3-2: Funding-stage heterogeneity (cross-sectional three-year window)
* Existing stage assignments include imputations; see stage_method.
preserve
use "C:/Users/user/Documents/VD/260122 winsorization_stage4.dta", clear
keep firm_id OrganizationName VD VDyear stage4 stage_inference_method
rename OrganizationName stage_name
rename VD stage_vd
rename VDyear stage_year
rename stage4 fundstage
rename stage_inference_method stage_method
tempfile funding_stages
save `funding_stages'
restore
merge 1:1 firm_id using `funding_stages', generate(stage_merge)
assert stage_merge == 3
assert OrganizationName == stage_name & VD == stage_vd & VDyear == stage_year
drop stage_merge stage_name stage_vd stage_year
label variable fundstage "Funding stage at initial VD date or control reference year"
label define fundstage_lbl 1 "Seed / pre-Series" 2 "Series A" 3 "Series B" 4 "Series C+", replace
label values fundstage fundstage_lbl
label variable stage_method "Reference-stage assignment method, including imputation"
notes fundstage: Highest prior Series; otherwise future-round backcast or round-order fallback.
notes fundstage: One grant-only firm was assumed Seed in source. Not an observed Series.
gen byte early_sb = inrange(fundstage,1,3) if !missing(fundstage)
label variable early_sb "1=Seed through Series B; 0=Series C+ at reference point"
tab fundstage VD, row
save "$OUT/table3_2_analysis.dta", replace

* Panel A: Seed-B versus C+, reconstructed from the four-stage measure.
reghdfe ln_grantedbyfiling_norm_win3 i.VD##ib0.early_sb ///
    i.priorpatentdummy_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store T32_binary
margins early_sb, dydx(1.VD) predict(xb)

* Panel B: stage-specific VD effects, using the current Table 3 outcome and FE.
reghdfe ln_grantedbyfiling_norm_win3 i.VD##ib1.fundstage ///
    i.priorpatentdummy_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store T32_stage
testparm 1.VD#2.fundstage 1.VD#3.fundstage 1.VD#4.fundstage
lincom 1.VD#4.fundstage - 1.VD#3.fundstage
margins fundstage, dydx(1.VD) predict(xb) post
estimates store T32_effects

* Also include the prior-patent interaction from Table 3 column 4.
reghdfe ln_grantedbyfiling_norm_win3 i.VD##ib1.fundstage ///
    i.VD##i.priorpatentdummy_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store T32_full
lincom 1.VD#4.fundstage - 1.VD#3.fundstage
margins fundstage, dydx(1.VD) predict(xb) post
estimates store T32_full_effects
esttab T32_binary T32_stage T32_full using "$OUT/Table3_2_coefficients.rtf", replace ///
    b(3) se(3) label stats(N r2) title("Table 3-2. Funding-stage heterogeneity")
esttab T32_effects T32_full_effects using "$OUT/Table3_2_stage_effects.rtf", replace ///
    b(3) se(3) label title("Table 3-2. Stage-specific VD marginal effects")
* End Table 3-2

display "T32_COMPLETE"
exit, clear

