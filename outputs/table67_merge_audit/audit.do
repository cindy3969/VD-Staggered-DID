version 19
clear all
set more off
log using "C:/Users/user/Documents/VD/outputs/table67_merge_audit/audit.log", text replace
postfile audit str12 source str16 model str60 term double b se p N failures using "C:/Users/user/Documents/VD/outputs/table67_merge_audit/estimates.dta", replace
program define record_model
syntax, Source(string) Model(string)
tempname B V
matrix `B'=e(b)
matrix `V'=e(V)
local names : colnames `B'
forvalues j=1/`=colsof(`B')' {
local term : word `j' of `names'
local se=sqrt(`V'[`j',`j'])
local prob=.
if `se'>0 & !missing(`se') {
if !missing(e(df_r)) local prob=2*ttail(e(df_r),abs(`B'[1,`j']/`se'))
else local prob=2*normal(-abs(`B'[1,`j']/`se'))
}
post audit ("`source'") ("`model'") ("`term'") (`B'[1,`j']) (`se') (`prob') (e(N)) (e(N_fail))
}
end
use "C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms/260122 winsorization.dta", clear
capture drop audit_prior
gen audit_prior=patentdummybyfiling
reghdfe ln_moneyraised_y1 VD i.audit_prior i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
record_model, source(legacy) model(T6_legacy_1)
reghdfe ln_moneyraised_y2 VD i.audit_prior i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
record_model, source(legacy) model(T6_legacy_2)
reghdfe ln_moneyraised_y3 VD i.audit_prior i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
record_model, source(legacy) model(T6_legacy_3)
stset VDage3, failure(acq3==1) id(firm_id)
stcox VD i.Region2 i.Industry2 i.Foundingyear, nohr
record_model, source(legacy) model(acq3_base)
stcox VD audit_prior earlystage ln_MoneyRaised_VD NumofFundingRounds_VD i.Region2 i.Industry2 i.Foundingyear, nohr
record_model, source(legacy) model(acq3_ctrl)
stset VDage3, failure(public3==1) id(firm_id)
stcox VD i.Region2 i.Industry2 i.Foundingyear, nohr
record_model, source(legacy) model(public3_base)
stcox VD audit_prior earlystage ln_MoneyRaised_VD NumofFundingRounds_VD i.Region2 i.Industry2 i.Foundingyear, nohr
record_model, source(legacy) model(public3_ctrl)
stset VDage3, failure(badexit3==1) id(firm_id)
stcox VD i.Region2 i.Industry2 i.Foundingyear, nohr
record_model, source(legacy) model(badexit3_base)
stcox VD audit_prior earlystage ln_MoneyRaised_VD NumofFundingRounds_VD i.Region2 i.Industry2 i.Foundingyear, nohr
record_model, source(legacy) model(badexit3_ctrl)
use "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_original_2820_cross_section_v2.dta", clear
capture drop audit_prior
gen audit_prior=patentdummybyfiling
reghdfe ln_moneyraised_y1 VD i.audit_prior i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
record_model, source(current) model(T6_legacy_1)
reghdfe ln_moneyraised_y2 VD i.audit_prior i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
record_model, source(current) model(T6_legacy_2)
reghdfe ln_moneyraised_y3 VD i.audit_prior i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
record_model, source(current) model(T6_legacy_3)
stset VDage3, failure(acq3==1) id(firm_id)
stcox VD i.Region2 i.Industry2 i.Foundingyear, nohr
record_model, source(current) model(acq3_base)
stcox VD audit_prior earlystage ln_MoneyRaised_VD NumofFundingRounds_VD i.Region2 i.Industry2 i.Foundingyear, nohr
record_model, source(current) model(acq3_ctrl)
stset VDage3, failure(public3==1) id(firm_id)
stcox VD i.Region2 i.Industry2 i.Foundingyear, nohr
record_model, source(current) model(public3_base)
stcox VD audit_prior earlystage ln_MoneyRaised_VD NumofFundingRounds_VD i.Region2 i.Industry2 i.Foundingyear, nohr
record_model, source(current) model(public3_ctrl)
stset VDage3, failure(badexit3==1) id(firm_id)
stcox VD i.Region2 i.Industry2 i.Foundingyear, nohr
record_model, source(current) model(badexit3_base)
stcox VD audit_prior earlystage ln_MoneyRaised_VD NumofFundingRounds_VD i.Region2 i.Industry2 i.Foundingyear, nohr
record_model, source(current) model(badexit3_ctrl)
capture drop audit_dv
gen audit_dv=ln(1+moneyraised_t1)
reghdfe audit_dv VD i.audit_prior i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
record_model, source(current) model(T6_new_1)
capture drop audit_dv
gen audit_dv=ln(1+moneyraised_t2)
reghdfe audit_dv VD i.audit_prior i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
record_model, source(current) model(T6_new_2)
capture drop audit_dv
gen audit_dv=ln(1+equityraised_t3)
reghdfe audit_dv VD i.audit_prior i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
record_model, source(current) model(T6_new_3)
postclose audit
display "AUDIT_COMPLETE"
log close
