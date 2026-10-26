version 19
clear all
set more off
log using "C:/Users/user/Documents/VD/outputs/table67_merge_audit/verify_screenshot.log", text replace
use "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_original_2820_cross_section_v2.dta", clear
forvalues h=1/3 {
reghdfe ln_moneyraised_y`h' VD i.patentdummybyfiling i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
}
foreach event in acq3 public3 badexit3 {
stset VDage3, failure(`event'==1) id(firm_id)
stcox VD, nohr
stcox VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2, nohr
}
display "SCREENSHOT_CHECK_COMPLETE"
log close
