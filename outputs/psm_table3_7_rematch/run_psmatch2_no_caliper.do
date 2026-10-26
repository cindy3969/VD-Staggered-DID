version 19
clear all
set more off
set seed 20250901
global OUT "C:/Users/user/Documents/VD/outputs/psm_table3_7_rematch"
capture log close
log using "$OUT/psmatch2_no_caliper.log", text replace
use "$OUT/psm_input_7316.dta", clear

capture confirm numeric variable Region2
if _rc encode Region2, gen(Region2_num)
else gen Region2_num=Region2
capture confirm numeric variable Industry2
if _rc encode Industry2, gen(Industry2_num)
else gen Industry2_num=Industry2

sort name_key OrganizationURL
psmatch2 VD_Backing ///
    ln_Total_Funding_Amount_FirstVD ///
    NumberOfFunding_Rounds_FirstVD ///
    Patents_VD ///
    i.Founding_Year ///
    TimeToFirst_VC ///
    i.Region2_num ///
    i.Industry2_num, ///
    logit neighbor(1) noreplacement common

gen byte matched=(_weight==1 & !missing(_weight))
count if matched
display "MATCHED TOTAL=" r(N)
count if matched & VD_Backing==1
display "MATCHED TREATED=" r(N)
count if matched & VD_Backing==0
display "MATCHED CONTROLS=" r(N)
save "$OUT/psmatch2_no_caliper_full7316.dta", replace
preserve
keep if matched
save "$OUT/psmatch2_no_caliper_matched.dta", replace
export delimited using "$OUT/psmatch2_no_caliper_matched.csv", replace
restore
log close
exit, clear
