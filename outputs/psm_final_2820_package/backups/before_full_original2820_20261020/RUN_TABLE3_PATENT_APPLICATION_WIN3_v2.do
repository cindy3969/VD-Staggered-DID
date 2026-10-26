version 19
clear all
set more off
set linesize 180
capture log close _all

* ORIGINAL sample: 260122 winsorization.dta, NOT rematched firms.
* Run this entire do-file (Ctrl+D). No PSM is performed.
* The new DTA preserves all 164 original columns, including original controls.
* Each outcome has (1) H1, (2) H2, (3) H3, (4) both interactions.
* Outcome window = reference VDyear+1 through VDyear+3, data through 2024.
* Use the original VDyear, treatment status, prior-patent and stage controls.
* Normalization matches the existing variables; no additional winsorization.
* Grant-rate scaling is not a guaranteed solution to right censoring.
* v4 is missing when there are no granted patents; do NOT replace it with 0.
* 190 firms lack a full 3-year follow-up. Flag retained; no silent exclusions.
* Generated tables use log(1+outcome), matching the previous analysis do-file.
* Raw outcomes remain available in the DTA.
* No existing input data or original analysis do-file is overwritten.

capture mkdir "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_original2820_results"
log using "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_original2820_results/RUN_TABLE3_v2.log", text replace
use "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_original_2820_cross_section_v2.dta", clear
isid firm_id
assert _N == 2820
count if VD==1
assert r(N)==1410
count if VD==0
assert r(N)==1410
assert Priorpatent_VD == patentdummybyfiling
assert Earlystage_VD == earlystage
assert nopriorpatentdummy_VD == 1-patentdummybyfiling
assert !missing(VD, Priorpatent_VD, Earlystage_VD, ln_MoneyRaised_VD, NumofFundingRounds_VD, Region2, Industry2, Foundingyear)

* Required installed commands. No automatic installation or updates.
which reghdfe
which esttab

label variable VD "VD"
label variable nopriorpatentdummy_VD "No prior patent at VD"
label variable Earlystage_VD "Early stage at VD"
label variable ln_MoneyRaised_VD "Log funding at VD (original control)"
label variable NumofFundingRounds_VD "Funding rounds at VD (original control)"

* Recalculate only in memory; the DTA already contains these log columns.
replace ln_grantedbyfiling_win3 = log(grantedpatentbyfiling_win3+1)
replace ln_grantedbyfiling_norm_win3 = log(grantedpatentbyfiling_norm_win3+1)
replace ln_norm_cite_perpat_win3_v4 = log(norm_cite_perpat_win3_v4+1)
tabulate VD
tabulate win3_complete_2024
summarize grantedpatentbyfiling_win3 grantedpatentbyfiling_norm_win3 norm_cite_perpat_win3_v4

********************************************************************************
* DV: Log(1 + granted applications)
* FE: original Region2, Industry2, Foundingyear. Robust standard errors.
********************************************************************************
estimates clear

* (1) H1: VD main effect, with both moderators as controls.
quietly reghdfe ln_grantedbyfiling_win3 i.VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store H1

* (2) H2: VD x no prior patent.
quietly reghdfe ln_grantedbyfiling_win3 i.VD##i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store H2

* (3) H3: VD x early stage.
quietly reghdfe ln_grantedbyfiling_win3 i.VD##i.Earlystage_VD i.nopriorpatentdummy_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store H3

* (4) Full: both interactions, with all lower-order terms.
quietly reghdfe ln_grantedbyfiling_win3 i.VD##i.nopriorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store Full

* Display the table in Stata; parentheses contain p-values.
esttab H1 H2 H3 Full, ///
    title("Log(1 + granted applications)") mtitles("H1" "H2" "H3" "Full") ///
    b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) nobaselevels noomitted ///
    order(1.VD 1.VD#1.nopriorpatentdummy_VD 1.VD#1.Earlystage_VD 1.nopriorpatentdummy_VD 1.Earlystage_VD ln_MoneyRaised_VD NumofFundingRounds_VD _cons) ///
    stats(N r2 r2_a, fmt(0 3 3) labels("Observations" "R-squared" "Adjusted R-squared"))

* Save a separate Word-readable RTF for this outcome.
esttab H1 H2 H3 Full using "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_original2820_results/Table3_granted_count.rtf", replace ///
    title("Log(1 + granted applications)") mtitles("H1" "H2" "H3" "Full") ///
    b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) nobaselevels noomitted ///
    order(1.VD 1.VD#1.nopriorpatentdummy_VD 1.VD#1.Earlystage_VD 1.nopriorpatentdummy_VD 1.Earlystage_VD ln_MoneyRaised_VD NumofFundingRounds_VD _cons) ///
    coeflabels(1.VD "VD (H1)" 1.VD#1.nopriorpatentdummy_VD "VD x No prior patent (H2)" 1.VD#1.Earlystage_VD "VD x Early stage (H3)" 1.nopriorpatentdummy_VD "No prior patent at VD" 1.Earlystage_VD "Early stage at VD" ln_MoneyRaised_VD "Log funding at VD" NumofFundingRounds_VD "Funding rounds at VD" _cons "Constant") ///
    stats(N r2 r2_a, fmt(0 3 3) labels("Observations" "R-squared" "Adjusted R-squared")) ///
    addnotes("Original 260122 sample; no rematching." "Region, industry and founding-year fixed effects in all columns." "Robust p-values in parentheses. * p<0.10; ** p<0.05; *** p<0.01." "Missing outcomes and absorbed-FE singletons can reduce regression N.")

********************************************************************************
* DV: Log(1 + normalized granted applications)
* FE: original Region2, Industry2, Foundingyear. Robust standard errors.
********************************************************************************
estimates clear

* (1) H1: VD main effect, with both moderators as controls.
quietly reghdfe ln_grantedbyfiling_norm_win3 i.VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store H1

* (2) H2: VD x no prior patent.
quietly reghdfe ln_grantedbyfiling_norm_win3 i.VD##i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store H2

* (3) H3: VD x early stage.
quietly reghdfe ln_grantedbyfiling_norm_win3 i.VD##i.Earlystage_VD i.nopriorpatentdummy_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store H3

* (4) Full: both interactions, with all lower-order terms.
quietly reghdfe ln_grantedbyfiling_norm_win3 i.VD##i.nopriorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store Full

* Display the table in Stata; parentheses contain p-values.
esttab H1 H2 H3 Full, ///
    title("Log(1 + normalized granted applications)") mtitles("H1" "H2" "H3" "Full") ///
    b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) nobaselevels noomitted ///
    order(1.VD 1.VD#1.nopriorpatentdummy_VD 1.VD#1.Earlystage_VD 1.nopriorpatentdummy_VD 1.Earlystage_VD ln_MoneyRaised_VD NumofFundingRounds_VD _cons) ///
    stats(N r2 r2_a, fmt(0 3 3) labels("Observations" "R-squared" "Adjusted R-squared"))

* Save a separate Word-readable RTF for this outcome.
esttab H1 H2 H3 Full using "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_original2820_results/Table3_normalized_granted_count.rtf", replace ///
    title("Log(1 + normalized granted applications)") mtitles("H1" "H2" "H3" "Full") ///
    b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) nobaselevels noomitted ///
    order(1.VD 1.VD#1.nopriorpatentdummy_VD 1.VD#1.Earlystage_VD 1.nopriorpatentdummy_VD 1.Earlystage_VD ln_MoneyRaised_VD NumofFundingRounds_VD _cons) ///
    coeflabels(1.VD "VD (H1)" 1.VD#1.nopriorpatentdummy_VD "VD x No prior patent (H2)" 1.VD#1.Earlystage_VD "VD x Early stage (H3)" 1.nopriorpatentdummy_VD "No prior patent at VD" 1.Earlystage_VD "Early stage at VD" ln_MoneyRaised_VD "Log funding at VD" NumofFundingRounds_VD "Funding rounds at VD" _cons "Constant") ///
    stats(N r2 r2_a, fmt(0 3 3) labels("Observations" "R-squared" "Adjusted R-squared")) ///
    addnotes("Original 260122 sample; no rematching." "Region, industry and founding-year fixed effects in all columns." "Robust p-values in parentheses. * p<0.10; ** p<0.05; *** p<0.01." "Missing outcomes and absorbed-FE singletons can reduce regression N.")

********************************************************************************
* DV: Log(1 + normalized citations per granted patent), v4
* FE: original Region2, Industry2, Foundingyear. Robust standard errors.
********************************************************************************
estimates clear

* (1) H1: VD main effect, with both moderators as controls.
quietly reghdfe ln_norm_cite_perpat_win3_v4 i.VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store H1

* (2) H2: VD x no prior patent.
quietly reghdfe ln_norm_cite_perpat_win3_v4 i.VD##i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store H2

* (3) H3: VD x early stage.
quietly reghdfe ln_norm_cite_perpat_win3_v4 i.VD##i.Earlystage_VD i.nopriorpatentdummy_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store H3

* (4) Full: both interactions, with all lower-order terms.
quietly reghdfe ln_norm_cite_perpat_win3_v4 i.VD##i.nopriorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store Full

* Display the table in Stata; parentheses contain p-values.
esttab H1 H2 H3 Full, ///
    title("Log(1 + normalized citations per granted patent), v4") mtitles("H1" "H2" "H3" "Full") ///
    b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) nobaselevels noomitted ///
    order(1.VD 1.VD#1.nopriorpatentdummy_VD 1.VD#1.Earlystage_VD 1.nopriorpatentdummy_VD 1.Earlystage_VD ln_MoneyRaised_VD NumofFundingRounds_VD _cons) ///
    stats(N r2 r2_a, fmt(0 3 3) labels("Observations" "R-squared" "Adjusted R-squared"))

* Save a separate Word-readable RTF for this outcome.
esttab H1 H2 H3 Full using "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_original2820_results/Table3_citation_quality_v4.rtf", replace ///
    title("Log(1 + normalized citations per granted patent), v4") mtitles("H1" "H2" "H3" "Full") ///
    b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) nobaselevels noomitted ///
    order(1.VD 1.VD#1.nopriorpatentdummy_VD 1.VD#1.Earlystage_VD 1.nopriorpatentdummy_VD 1.Earlystage_VD ln_MoneyRaised_VD NumofFundingRounds_VD _cons) ///
    coeflabels(1.VD "VD (H1)" 1.VD#1.nopriorpatentdummy_VD "VD x No prior patent (H2)" 1.VD#1.Earlystage_VD "VD x Early stage (H3)" 1.nopriorpatentdummy_VD "No prior patent at VD" 1.Earlystage_VD "Early stage at VD" ln_MoneyRaised_VD "Log funding at VD" NumofFundingRounds_VD "Funding rounds at VD" _cons "Constant") ///
    stats(N r2 r2_a, fmt(0 3 3) labels("Observations" "R-squared" "Adjusted R-squared")) ///
    addnotes("Original 260122 sample; no rematching." "Region, industry and founding-year fixed effects in all columns." "Robust p-values in parentheses. * p<0.10; ** p<0.05; *** p<0.01." "Missing outcomes and absorbed-FE singletons can reduce regression N.")

display as result "COMPLETED: original 2820 sample, three outcomes x four models."
log close

