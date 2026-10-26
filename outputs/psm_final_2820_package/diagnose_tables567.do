version 19
clear all
set more off
set linesize 255
log using "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/diagnose_tables567.log", text replace
use "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_original_2820_cross_section_v2.dta", clear
quietly reghdfe ln_moneyraised_win3 VD i.patentdummybyfiling i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
display "AUDIT T5 1 VD=" _b[VD] " N=" e(N) " R2=" e(r2) " constant=" _b[_cons]
quietly reghdfe ln_moneyraised_win3 i.VD##i.patentdummybyfiling i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
display "AUDIT T5 2 VD=" _b[1.VD] " N=" e(N) " R2=" e(r2) " constant=" _b[_cons]
quietly reghdfe ln_moneyraised_win3 i.patentdummybyfiling i.VD##i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
display "AUDIT T5 3 VD=" _b[1.VD] " N=" e(N) " R2=" e(r2) " constant=" _b[_cons]
quietly reghdfe ln_moneyraised_win3 i.VD##i.patentdummybyfiling i.VD##i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
display "AUDIT T5 4 VD=" _b[1.VD] " N=" e(N) " R2=" e(r2) " constant=" _b[_cons]
quietly reghdfe ln_moneyraised_y1 VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
display "AUDIT T6 1 VD=" _b[VD] " p=" 2*ttail(e(df_r),abs(_b[VD]/_se[VD])) " N=" e(N) " R2=" e(r2)
quietly reghdfe ln_moneyraised_y2 VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
display "AUDIT T6 2 VD=" _b[VD] " p=" 2*ttail(e(df_r),abs(_b[VD]/_se[VD])) " N=" e(N) " R2=" e(r2)
quietly reghdfe ln_moneyraised_y3 VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
display "AUDIT T6 3 VD=" _b[VD] " p=" 2*ttail(e(df_r),abs(_b[VD]/_se[VD])) " N=" e(N) " R2=" e(r2)
quietly stset VDage3, failure(acq3==1)
quietly stcox VD, nohr
display "AUDIT T7 acq3 VD VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
quietly stset VDage3, failure(acq3==1)
quietly stcox VD Foundingyear ib4.Region2 ib3.Industry2, nohr
display "AUDIT T7 acq3 VD Foundingyear ib4.Region2 ib3.Industry2 VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
quietly stset VDage3, failure(acq3==1)
quietly stcox VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2, nohr
display "AUDIT T7 acq3 VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2 VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
quietly stset VDage3, failure(public3==1)
quietly stcox VD, nohr
display "AUDIT T7 public3 VD VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
quietly stset VDage3, failure(public3==1)
quietly stcox VD Foundingyear ib4.Region2 ib3.Industry2, nohr
display "AUDIT T7 public3 VD Foundingyear ib4.Region2 ib3.Industry2 VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
quietly stset VDage3, failure(public3==1)
quietly stcox VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2, nohr
display "AUDIT T7 public3 VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2 VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
quietly stset VDage3, failure(badexit3==1)
quietly stcox VD, nohr
display "AUDIT T7 badexit3 VD VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
quietly stset VDage3, failure(badexit3==1)
quietly stcox VD Foundingyear ib4.Region2 ib3.Industry2, nohr
display "AUDIT T7 badexit3 VD Foundingyear ib4.Region2 ib3.Industry2 VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
quietly stset VDage3, failure(badexit3==1)
quietly stcox VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2, nohr
display "AUDIT T7 badexit3 VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2 VD=" _b[VD] " p=" 2*normal(-abs(_b[VD]/_se[VD])) " N=" e(N) " failures=" e(N_fail)
log close
exit, clear

