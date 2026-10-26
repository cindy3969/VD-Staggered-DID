clear all
set more off
log using "C:/Users/user/Documents/VD/outputs/iv_regional_supply/add_supply.log", replace text
use "C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms/260122 winsorization.dta", clear
keep Region2 VDyear numberofvddeals vdsupply
duplicates drop
isid Region2 VDyear
tempfile supply
save `supply'
use "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_current_2820_cross_section_v2.dta", clear
gen long __original_order = _n
merge m:1 Region2 VDyear using `supply', keep(master match) assert(match) nogen
assert !missing(numberofvddeals, vdsupply)
sort __original_order
drop __original_order
assert _N == 2820
save "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_current_2820_cross_section_v2.dta", replace
log close
