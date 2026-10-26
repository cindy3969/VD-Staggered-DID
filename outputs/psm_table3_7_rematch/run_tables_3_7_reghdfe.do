version 19
clear all
set more off
global OUT "C:/Users/user/Documents/VD/outputs/psm_table3_7_rematch"
capture log close
log using "$OUT/tables_3_7_reghdfe.log", text replace
use "$OUT/rematched_2820_cross_section.dta", clear

local controls "patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear"
local absorb_fe "Region2 Industry2"

* Table 3. Patent quantity
eststo clear
eststo m1: reghdfe ln_patentbyfiling_win3 VD patentdummybyfiling earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear, ///
    absorb(Region2 Industry2) vce(robust)
eststo m2: reghdfe ln_patentbyfiling_win3 c.VD##c.patentdummybyfiling earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear, absorb(`absorb_fe') vce(robust)
eststo m3: reghdfe ln_patentbyfiling_win3 patentdummybyfiling c.VD##c.earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear, absorb(`absorb_fe') vce(robust)
eststo m4: reghdfe ln_patentbyfiling_win3 c.VD##c.patentdummybyfiling c.VD##c.earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear, absorb(`absorb_fe') vce(robust)
foreach m in m1 m2 m3 m4 {
    estadd local RegionFE "Yes" : `m'
    estadd local IndustryFE "Yes" : `m'
    estadd local YearFE "Yes" : `m'
}
esttab m1 m2 m3 m4 using "$OUT/Table3.csv", replace csv b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    noomitted nobaselevels drop(Foundingyear) order(VD c.VD#c.patentdummybyfiling c.VD#c.earlystage patentdummybyfiling earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD _cons) ///
    stats(RegionFE IndustryFE YearFE N r2, labels("Region FE" "Industry FE" "Founding year control" "Observations" "R-squared") fmt(%s %s %s 0 3))
esttab m1 m2 m3 m4 using "$OUT/Table3.rtf", replace rtf b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    noomitted nobaselevels drop(Foundingyear) order(VD c.VD#c.patentdummybyfiling c.VD#c.earlystage patentdummybyfiling earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD _cons) ///
    stats(RegionFE IndustryFE YearFE N r2, labels("Region FE" "Industry FE" "Founding year control" "Observations" "R-squared") fmt(%s %s %s 0 3)) title("Table 3  Patent quantity")

* Table 4. Patent quality
eststo clear
eststo m1: reghdfe ln_fwd_norm_cohort_win3 VD `controls', absorb(`absorb_fe') vce(robust)
eststo m2: reghdfe ln_fwd_norm_cohort_win3 c.VD##c.patentdummybyfiling earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear, absorb(`absorb_fe') vce(robust)
eststo m3: reghdfe ln_fwd_norm_cohort_win3 patentdummybyfiling c.VD##c.earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear, absorb(`absorb_fe') vce(robust)
eststo m4: reghdfe ln_fwd_norm_cohort_win3 c.VD##c.patentdummybyfiling c.VD##c.earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear, absorb(`absorb_fe') vce(robust)
foreach m in m1 m2 m3 m4 {
    estadd local RegionFE "Yes" : `m'
    estadd local IndustryFE "Yes" : `m'
    estadd local YearFE "Yes" : `m'
}
esttab m1 m2 m3 m4 using "$OUT/Table4.csv", replace csv b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    noomitted nobaselevels drop(Foundingyear) order(VD c.VD#c.patentdummybyfiling c.VD#c.earlystage patentdummybyfiling earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD _cons) ///
    stats(RegionFE IndustryFE YearFE N r2, labels("Region FE" "Industry FE" "Founding year control" "Observations" "R-squared") fmt(%s %s %s 0 3))
esttab m1 m2 m3 m4 using "$OUT/Table4.rtf", replace rtf b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    noomitted nobaselevels drop(Foundingyear) order(VD c.VD#c.patentdummybyfiling c.VD#c.earlystage patentdummybyfiling earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD _cons) ///
    stats(RegionFE IndustryFE YearFE N r2, labels("Region FE" "Industry FE" "Founding year control" "Observations" "R-squared") fmt(%s %s %s 0 3)) title("Table 4  Patent quality")

* Table 5. Cumulative follow-on equity through t+3
eststo clear
eststo m1: reghdfe ln_moneyraised_win3 VD `controls', absorb(`absorb_fe') vce(robust)
eststo m2: reghdfe ln_moneyraised_win3 c.VD##c.patentdummybyfiling earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear, absorb(`absorb_fe') vce(robust)
eststo m3: reghdfe ln_moneyraised_win3 patentdummybyfiling c.VD##c.earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear, absorb(`absorb_fe') vce(robust)
eststo m4: reghdfe ln_moneyraised_win3 c.VD##c.patentdummybyfiling c.VD##c.earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear, absorb(`absorb_fe') vce(robust)
foreach m in m1 m2 m3 m4 {
    estadd local RegionFE "Yes" : `m'
    estadd local IndustryFE "Yes" : `m'
    estadd local YearFE "Yes" : `m'
}
esttab m1 m2 m3 m4 using "$OUT/Table5.csv", replace csv b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    noomitted nobaselevels drop(Foundingyear) order(VD c.VD#c.patentdummybyfiling c.VD#c.earlystage patentdummybyfiling earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD _cons) ///
    stats(RegionFE IndustryFE YearFE N r2, labels("Region FE" "Industry FE" "Founding year control" "Observations" "R-squared") fmt(%s %s %s 0 3))
esttab m1 m2 m3 m4 using "$OUT/Table5.rtf", replace rtf b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    noomitted nobaselevels drop(Foundingyear) order(VD c.VD#c.patentdummybyfiling c.VD#c.earlystage patentdummybyfiling earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD _cons) ///
    stats(RegionFE IndustryFE YearFE N r2, labels("Region FE" "Industry FE" "Founding year control" "Observations" "R-squared") fmt(%s %s %s 0 3)) title("Table 5  Follow-on equity raised")

* Table 6. Annual follow-on equity at t+1, t+2, and t+3
eststo clear
eststo m1: reghdfe ln_moneyraised_y1 VD `controls', absorb(`absorb_fe') vce(robust)
eststo m2: reghdfe ln_moneyraised_y2 VD `controls', absorb(`absorb_fe') vce(robust)
eststo m3: reghdfe ln_moneyraised_y3 VD `controls', absorb(`absorb_fe') vce(robust)
foreach m in m1 m2 m3 {
    estadd local RegionFE "Yes" : `m'
    estadd local IndustryFE "Yes" : `m'
    estadd local YearFE "Yes" : `m'
}
esttab m1 m2 m3 using "$OUT/Table6.csv", replace csv b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    drop(Foundingyear) order(VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD _cons) ///
    stats(RegionFE IndustryFE YearFE N r2, labels("Region FE" "Industry FE" "Founding year control" "Observations" "R-squared") fmt(%s %s %s 0 3))
esttab m1 m2 m3 using "$OUT/Table6.rtf", replace rtf b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    drop(Foundingyear) order(VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD _cons) ///
    stats(RegionFE IndustryFE YearFE N r2, labels("Region FE" "Industry FE" "Founding year control" "Observations" "R-squared") fmt(%s %s %s 0 3)) title("Table 6  Annual follow-on equity raised")

* Table 7. Cox models. stcox cannot use absorb(), so FE indicators enter explicitly.
preserve
keep if exit_history_available==1 & !missing(VDage3)
eststo clear
foreach event in acq3 public3 badexit3 {
    stset VDage3, failure(`event'==1)
    eststo `event'_1: stcox VD, vce(robust) nohr
    eststo `event'_2: stcox VD patentdummybyfiling earlystage ln_MoneyRaised_VD ///
        NumofFundingRounds_VD Foundingyear i.Region2 i.Industry2, vce(robust) nohr
}
foreach m in acq3_1 acq3_2 public3_1 public3_2 badexit3_1 badexit3_2 {
    estadd local RegionFE "Yes" : `m'
    estadd local IndustryFE "Yes" : `m'
    estadd local YearFE "Yes" : `m'
}
esttab acq3_1 acq3_2 public3_1 public3_2 badexit3_1 badexit3_2 using "$OUT/Table7.csv", ///
    replace csv b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) order(VD patentdummybyfiling earlystage ln_MoneyRaised_VD ///
    NumofFundingRounds_VD Foundingyear) stats(RegionFE IndustryFE YearFE N_fail N, labels("Region FE" "Industry FE" "Founding year control" "# of failures" "Observations") fmt(%s %s %s 0 0))
esttab acq3_1 acq3_2 public3_1 public3_2 badexit3_1 badexit3_2 using "$OUT/Table7.rtf", ///
    replace rtf b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) order(VD patentdummybyfiling earlystage ln_MoneyRaised_VD ///
    NumofFundingRounds_VD Foundingyear) stats(RegionFE IndustryFE YearFE N_fail N, labels("Region FE" "Industry FE" "Founding year control" "# of failures" "Observations") fmt(%s %s %s 0 0)) ///
    mtitles("M&A (1)" "M&A (2)" "IPO (3)" "IPO (4)" "Defunct (5)" "Defunct (6)") ///
    title("Table 7  Exit outcomes")
restore

log close
exit, clear
