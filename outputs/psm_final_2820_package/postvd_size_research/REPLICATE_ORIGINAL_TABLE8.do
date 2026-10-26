clear all
use "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/postvd_size_research/recovered_table8_original_611.dta", clear
* Original sample and covariates; employee measurement date is unverified.
regress emp2025_2 VD i.lastdeal2vd1, vce(robust)
estimates store table8_1
regress emp2025_2 VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD i.lastdeal2vd1 i.Founding_Year ib4.Region2 ib3.Industry2, vce(robust)
estimates store table8_2
regress emp2025_2 i.VD##ib0.patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD i.lastdeal2vd1 i.Founding_Year ib4.Region2 ib3.Industry2, vce(robust)
estimates store table8_3
regress emp2025_2 patentdummybyfiling i.VD##ib0.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD i.lastdeal2vd1 i.Founding_Year ib4.Region2 ib3.Industry2, vce(robust)
estimates store table8_4
regress emp2025_2 i.VD##ib0.patentdummybyfiling i.VD##ib0.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD i.lastdeal2vd1 i.Founding_Year ib4.Region2 ib3.Industry2, vce(robust)
estimates store table8_5
