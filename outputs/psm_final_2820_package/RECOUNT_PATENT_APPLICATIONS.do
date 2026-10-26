version 19
clear all
set more off

global ROOT "C:/Users/user/Documents/VD/outputs/psm_final_2820_package"
global DIAG "$ROOT/replicated_appendix"
global APPUNION "C:/Users/user/Documents/VD/outputs/csdid_union_corrected_3yr/application_level_union_corrected_visible_mismatches.csv"

use "$ROOT/psm_stata_full7316_with_scores.dta", clear

tempfile master reference counts
capture drop patent_application_VD patent_application_win3 name_key
gen str244 name_key=ustrlower(OrganizationName)
replace name_key=ustrregexra(name_key,"[^a-z0-9]","")

preserve
    keep name_key VDYear
    rename VDYear reference_year
    bysort name_key: egen reference_min=min(reference_year)
    bysort name_key: egen reference_max=max(reference_year)
    assert reference_min==reference_max
    bysort name_key: keep if _n==1
    drop reference_min reference_max
    save `reference', replace
restore
save `master', replace

import delimited using "$APPUNION", clear varnames(1) encoding(utf8)
keep if inrange(filing_year,2010,2024)
duplicates drop full_firm_id application_id, force
count
assert r(N)==39249
gen str244 name_key=ustrlower(organization_name)
replace name_key=ustrregexra(name_key,"[^a-z0-9]","")
merge m:1 name_key using `reference', keep(match) nogen
gen byte app_at_vd=(filing_year<=reference_year)
gen byte app_win3=inrange(filing_year-reference_year,0,3)
collapse (sum) patent_application_VD=app_at_vd ///
               patent_application_win3=app_win3, by(name_key)
save `counts', replace

use `master', clear
merge m:1 name_key using `counts', keep(master match) gen(_merge_appcounts)
replace patent_application_VD=0 if missing(patent_application_VD)
replace patent_application_win3=0 if missing(patent_application_win3)
label var patent_application_VD "Applications filed through actual or hypothetical VD year"
label var patent_application_win3 "Applications filed in years t=0 to t+3"

assert patent_application_VD==38 & patent_application_win3==16 if OrganizationName=="AliveCor"
assert patent_application_VD==9 & patent_application_win3==0 if OrganizationName=="Health Outcomes Sciences"

preserve
    keep no OrganizationName VD_Backing Founding_Year VDYear Grant_VD ///
         Grant_3years patent_application_VD patent_application_win3 ///
         _merge_appcounts matched_2820
    sort OrganizationName
    export delimited using "$DIAG/patent_application_count_audit.csv", replace
restore

drop _merge_appcounts
save "$ROOT/psm_stata_full7316_with_scores.dta", replace
preserve
    keep if matched_2820==1
    save "$ROOT/psm_stata_matched_2820.dta", replace
    export delimited using "$ROOT/psm_stata_matched_2820.csv", replace
restore

exit, clear
