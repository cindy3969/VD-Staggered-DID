version 19
clear all
set more off
global ROOT "C:/Users/user/Documents/VD"
global OUT "$ROOT/outputs/psm_table3_7_rematch"
capture log close
log using "$OUT/diagnose_r2.log", text replace

display "===== ARCHIVED 2820 DATA ====="
use "$ROOT/260122 winsorization_stage4.dta", clear
summarize ln_patentbyfiling_win3, detail
reghdfe ln_patentbyfiling_win3 VD patentdummybyfiling earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear, ///
    absorb(Region2 Industry2) vce(robust)
display "archived reghdfe e(r2)=" %9.6f e(r2) " within=" %9.6f e(r2_within)
reg ln_patentbyfiling_win3 VD patentdummybyfiling earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear i.Region2 i.Industry2, vce(robust)
display "archived reg e(r2)=" %9.6f e(r2)

display "===== NEW REMATCHED 2820 DATA ====="
use "$OUT/rematched_2820_cross_section.dta", clear
summarize ln_patentbyfiling_win3, detail
reghdfe ln_patentbyfiling_win3 VD patentdummybyfiling earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear, ///
    absorb(Region2 Industry2) vce(robust)
display "new reghdfe e(r2)=" %9.6f e(r2) " within=" %9.6f e(r2_within)
reg ln_patentbyfiling_win3 VD patentdummybyfiling earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear i.Region2 i.Industry2, vce(robust)
display "new reg e(r2)=" %9.6f e(r2)

log close
exit, clear
