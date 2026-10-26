version 19
clear all
set more off
capture log close
log using "C:/Users/user/Documents/VD/outputs/innovation_original2820_rebuild_20261020/merge_validation.log", text replace
use "C:/Users/user/Documents/VD/outputs/innovation_original2820_rebuild_20261020/innovation_update.dta", clear
isid firm_id
assert _N==2820
ds firm_id, not
local update_variables `r(varlist)'
use "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_original_2820_cross_section_v2.dta", clear
foreach variable of local update_variables {
    capture drop `variable'
}
merge 1:1 firm_id using "C:/Users/user/Documents/VD/outputs/innovation_original2820_rebuild_20261020/innovation_update.dta", assert(3) nogen
isid firm_id
assert _N==2820
sort firm_id
save "C:/Users/user/Documents/VD/outputs/innovation_original2820_rebuild_20261020/validated_candidate.dta", replace
log close
