clear all
set more off
use "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_current_2820_cross_section_v2.dta", clear

* Requires installed ivreghdfe, ivreg2, ranktest, reghdfe, ftools, outreg2.
* Granted applications: raw count, logged as ln(1 + count).
gen double ln_granted_iv = ln(1 + grantedpatentbyfiling_win3)
gen double ln_vdsupply = ln(1 + vdsupply)
gen double ln_numberofvddeals = ln(1 + numberofvddeals)

local controls i.priorpatentdummy_VD i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD
* Foundingyear FE follows the existing specification; it is NOT VDyear FE.
local fe Region2 Industry2 Foundingyear
local output "C:/Users/user/Documents/VD/outputs/iv_regional_supply/Table_A1_2SLS.xls"

* Column (1): second stage.
ivreghdfe ln_granted_iv `controls' (VD = ln_vdsupply), absorb(`fe') robust first
estimates store IV_second
gen byte iv_sample = e(sample)
scalar CD_F = e(cdf)
scalar KP_F = e(widstat)
outreg2 using "`output'", replace excel dec(3) pvalue ctitle(2SLS) ///
    addtext(Region FE, Yes, Industry FE, Yes, Founding-year FE, Yes) ///
    addstat(Cragg-Donald Wald F, CD_F, Kleibergen-Paap rk Wald F, KP_F)

* Column (2): first stage on exactly the same estimation sample.
reghdfe VD ln_vdsupply `controls' if iv_sample, absorb(`fe') vce(robust)
test ln_vdsupply
scalar excluded_IV_F = r(F)
outreg2 using "`output'", append excel dec(3) pvalue ctitle(First stage) ///
    addtext(Region FE, Yes, Industry FE, Yes, Founding-year FE, Yes) ///
    addstat(Excluded instrument robust F, excluded_IV_F)
estimates store IV_first

* Count-IV alternative: replace ln_vdsupply with ln_numberofvddeals throughout.
* For calendar-year FE instead, add VDyear to local fe above.
