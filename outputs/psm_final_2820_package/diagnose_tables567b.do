version 19
clear all
set more off
set linesize 255
log using "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/diagnose_tables567b.log", text replace
use "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_original_2820_cross_section_v2.dta", clear
quietly reghdfe ln_moneyraised_y1 VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
display "AUDIT T6 1 R2=" e(r2) " AdjR2=" e(r2_a) " within=" e(r2_within)
quietly reghdfe ln_moneyraised_y2 VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
display "AUDIT T6 2 R2=" e(r2) " AdjR2=" e(r2_a) " within=" e(r2_within)
quietly reghdfe ln_moneyraised_y3 VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
display "AUDIT T6 3 R2=" e(r2) " AdjR2=" e(r2_a) " within=" e(r2_within)
quietly stset VDage3, failure(acq3==1)
quietly stcox VD Region2 Industry2 Foundingyear, nohr
display "AUDIT T7 acq3 VD Region2 Industry2 Foundingyear VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
quietly stset VDage3, failure(acq3==1)
quietly stcox VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Region2 Industry2 Foundingyear, nohr
display "AUDIT T7 acq3 VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Region2 Industry2 Foundingyear VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
quietly stset VDage3, failure(public3==1)
quietly stcox VD Region2 Industry2 Foundingyear, nohr
display "AUDIT T7 public3 VD Region2 Industry2 Foundingyear VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
quietly stset VDage3, failure(public3==1)
quietly stcox VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Region2 Industry2 Foundingyear, nohr
display "AUDIT T7 public3 VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Region2 Industry2 Foundingyear VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
quietly stset VDage3, failure(badexit3==1)
quietly stcox VD Region2 Industry2 Foundingyear, nohr
display "AUDIT T7 badexit3 VD Region2 Industry2 Foundingyear VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
quietly stset VDage3, failure(badexit3==1)
quietly stcox VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Region2 Industry2 Foundingyear, nohr
display "AUDIT T7 badexit3 VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Region2 Industry2 Foundingyear VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
quietly stset VDage3, failure(acq3==1)
quietly stcox VD i.Region2 i.Industry2 i.Foundingyear, nohr
display "AUDIT CATEGORICAL acq3 VD i.Region2 i.Industry2 i.Foundingyear VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
quietly stset VDage3, failure(acq3==1)
quietly stcox VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD i.Region2 i.Industry2 i.Foundingyear, nohr
display "AUDIT CATEGORICAL acq3 VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD i.Region2 i.Industry2 i.Foundingyear VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
quietly stset VDage3, failure(public3==1)
quietly stcox VD i.Region2 i.Industry2 i.Foundingyear, nohr
display "AUDIT CATEGORICAL public3 VD i.Region2 i.Industry2 i.Foundingyear VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
quietly stset VDage3, failure(public3==1)
quietly stcox VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD i.Region2 i.Industry2 i.Foundingyear, nohr
display "AUDIT CATEGORICAL public3 VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD i.Region2 i.Industry2 i.Foundingyear VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
quietly stset VDage3, failure(badexit3==1)
quietly stcox VD i.Region2 i.Industry2 i.Foundingyear, nohr
display "AUDIT CATEGORICAL badexit3 VD i.Region2 i.Industry2 i.Foundingyear VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
quietly stset VDage3, failure(badexit3==1)
quietly stcox VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD i.Region2 i.Industry2 i.Foundingyear, nohr
display "AUDIT CATEGORICAL badexit3 VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD i.Region2 i.Industry2 i.Foundingyear VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
log close
exit, clear

