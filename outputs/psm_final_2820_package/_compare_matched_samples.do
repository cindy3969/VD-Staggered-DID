version 19
clear all
set more off
global PKG "C:/Users/user/Documents/VD/outputs/psm_final_2820_package"
global BASE "C:/Users/user/Documents/VD/outputs/psm_rematch_rebuilt"
log using "$PKG/matched_sample_comparison.log", text replace

tempfile OLD NEW

use "$PKG/ORIGINAL_final_matched_2820.dta", clear
keep OrganizationName VD
rename OrganizationName organization_name
gen str100 name_key=ustrlower(ustrtrim(organization_name))
replace name_key=ustrregexra(name_key,"[^a-z0-9]","")
duplicates drop name_key VD, force
rename VD old_treated
save `OLD'

use "$BASE/psm_matched_2820.dta", clear
keep organization_name vd_backed
gen str100 name_key=ustrlower(ustrtrim(organization_name))
replace name_key=ustrregexra(name_key,"[^a-z0-9]","")
duplicates drop name_key vd_backed, force
rename vd_backed new_treated
save `NEW'

use `OLD', clear
merge 1:1 name_key using `NEW'

gen byte old_control=old_treated==0 if !missing(old_treated)
gen byte new_control=new_treated==0 if !missing(new_treated)
gen byte old_treat=old_treated==1 if !missing(old_treated)
gen byte new_treat=new_treated==1 if !missing(new_treated)

display as text _newline "OVERLAP COUNTS"
count if old_control==1
display "Old controls: " r(N)
count if new_control==1
display "New controls: " r(N)
count if old_control==1 & new_control==1
display "Controls in both: " r(N)
count if old_control==1 & new_control!=1
display "Old controls not retained: " r(N)
count if new_control==1 & old_control!=1
display "New replacement controls: " r(N)

count if old_treat==1
display "Old treated: " r(N)
count if new_treat==1
display "New treated: " r(N)
count if old_treat==1 & new_treat==1
display "Treated in both: " r(N)
count if old_treat==1 & new_treat!=1
display "Old treated not retained as treated: " r(N)
count if new_treat==1 & old_treat!=1
display "New treated not formerly treated: " r(N)

preserve
keep if (old_control==1 & new_control!=1) | (new_control==1 & old_control!=1) | ///
        (old_treat==1 & new_treat!=1) | (new_treat==1 & old_treat!=1)
keep organization_name name_key old_treated new_treated _merge
export delimited using "$PKG/matched_sample_membership_changes.csv", replace
restore

log close
exit, clear
