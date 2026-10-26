version 19
clear all
set more off
global P "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected"
capture confirm file "$P/citation_quality_20261019/original_panel_backup.dta"
if _rc copy "$P/firm_year_all_applications_and_truncation_specs.dta" "$P/citation_quality_20261019/original_panel_backup.dta"
use "$P/firm_year_all_applications_and_truncation_specs.dta", clear
foreach newvar in citation_quality_npat norm_cite_perpat_v1 norm_cite_perpat_v2 norm_cite_perpat_v3 norm_cite_perpat_v4 {
    capture drop `newvar'
}
merge 1:1 full_firm_id year using "$P/citation_quality_20261019/annual_quality_addon.dta", assert(match) nogen
isid full_firm_id year
assert _N==88547
save "$P/firm_year_all_applications_and_truncation_specs.dta", replace
export delimited using "$P/firm_year_all_applications_and_truncation_specs.csv", replace
exit, clear
