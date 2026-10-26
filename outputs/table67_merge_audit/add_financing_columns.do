version 19
clear all
set more off
log using "C:/Users/user/Documents/VD/outputs/table67_merge_audit/add_financing_columns.log", text replace
use "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_original_2820_cross_section_v2.dta", clear
isid firm_id
assert _N==2820
sort firm_id
unab original_columns : _all
tempfile unchanged
save `unchanged'
merge 1:1 firm_id using "C:/Users/user/Documents/VD/outputs/downstream_financing/financing_support.dta", keepusing(next_n next_disclosed next_amount observed next_event followup_days next_days duration_days complete1 raise1 cum1 undisclosed1 complete2 raise2 cum2 undisclosed2 complete3 raise3 cum3 undisclosed3) assert(match) nogen
merge 1:1 firm_id using "C:/Users/user/Documents/VD/260122 winsorization_stage4.dta", keepusing(stage4 stage_inference_method) assert(match) nogen
gen byte latestage_VD = (stage4==4) if !missing(stage4)
label variable latestage_VD "Series C+ at VD/reference date (stage4; includes imputation)"
assert priorpatentdummy_VD==patentdummybyfiling
assert Earlystage_VD==earlystage
forvalues h=1/3 {
assert missing(raise`h') if complete`h'==0
assert missing(cum`h') if undisclosed`h'==1
}
sort firm_id
cf `original_columns' using `unchanged', all
assert _N==2820
isid firm_id
save "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_original_2820_cross_section_v2.dta", replace
display "COLUMN_ADDITION_COMPLETE"
log close
