version 19
clear all
set more off
set seed 20261011

global PKG "C:/Users/user/Documents/VD/outputs/psm_final_2820_package"
global SRC  "C:/Users/user/Documents/VD/outputs/csdid_ultimately_granted_primary/csdid_ultimately_granted_full7316_controls.dta"
global OUT  "$PKG/legacy_aligned_rematch"
capture mkdir "$OUT"

capture log close
log using "$OUT/REBUILD_PSM_LEGACY_ALIGNED.log", text replace

********************************************************************************
* 1. RESTORE THE HISTORICAL TREATMENT DEFINITION
********************************************************************************
use "$SRC", clear

gen str100 name_key=ustrlower(ustrtrim(organization_name))
replace name_key=ustrregexra(name_key,"[^a-z0-9]","")

replace vd_backed=1 if inlist(name_key,"dermira","eargo")
replace vd_backed=0 if inlist(name_key,"cortex","nomi1")
replace first_vd_year=. if inlist(name_key,"cortex","nomi1")
replace g_first_vd=0 if inlist(name_key,"cortex","nomi1")

count if vd_backed==1
assert r(N)==1440

********************************************************************************
* 2. HISTORICAL 1:1 PSM SPECIFICATION
* Same score model used in the historical do-file:
* founding year FE, industry, reference-year funding rounds and funding amount,
* region, and years from founding to first VC.
********************************************************************************
capture which psmatch2
if _rc {
    display as error "psmatch2 is not installed. Run: ssc install psmatch2"
    exit 199
}

sort full_firm_id
psmatch2 vd_backed i.founding_year ib4.industry2 funding_rounds_ref ///
    ln_funding_ref ib4.region2 time_first_vc, ///
    neighbor(1) logit noreplacement

gen byte psm_esample=!missing(_pscore)
gen byte psm_matched=(_weight>0 & !missing(_weight))
replace psm_matched=1 if vd_backed==1 & psm_esample

count if vd_backed==1 & psm_esample
assert r(N)==1410
count if vd_backed==1 & psm_matched
assert r(N)==1410
count if vd_backed==0 & psm_matched
assert r(N)==1410

save "$OUT/legacy_aligned_full7316_with_scores.dta", replace
preserve
    keep if psm_matched
    save "$OUT/legacy_aligned_matched_2820.dta", replace
    export delimited using "$OUT/legacy_aligned_matched_2820.csv", replace
restore

********************************************************************************
* 3. COMPARE MEMBERSHIP WITH THE ARCHIVED ORIGINAL 2,820 SAMPLE
********************************************************************************
tempfile OLD NEW
preserve
    use "$PKG/ORIGINAL_final_matched_2820.dta", clear
    keep OrganizationName VD
    rename OrganizationName organization_name
    gen str100 name_key=ustrlower(ustrtrim(organization_name))
    replace name_key=ustrregexra(name_key,"[^a-z0-9]","")
    duplicates drop name_key VD, force
    rename VD old_treated
    save `OLD'
restore

********************************************************************************
* 3A. EXACTLY RESTORE THE ARCHIVED 2,820-FIRM MEMBERSHIP
* Re-estimated scores are retained, but sample membership is fixed to the
* archived matched sample so the manuscript analyses remain reproducible.
********************************************************************************
preserve
    merge m:1 name_key using `OLD', keep(master match) nogen
    sort name_key full_firm_id
    gen byte legacy_exact_sample=(!missing(old_treated) & old_treated==vd_backed)
    by name_key: gen int legacy_name_rank=sum(legacy_exact_sample)
    replace legacy_exact_sample=0 if legacy_exact_sample & legacy_name_rank>1
    drop legacy_name_rank
    count if legacy_exact_sample
    assert r(N)==2820
    rename psm_matched selected_by_fresh_rematch
    gen byte psm_matched=legacy_exact_sample
    save "$OUT/legacy_aligned_full7316_EXACT_membership.dta", replace
    keep if legacy_exact_sample
    assert old_treated==vd_backed
    count if vd_backed==1
    assert r(N)==1410
    count if vd_backed==0
    assert r(N)==1410
    save "$OUT/EXACT_original_membership_2820_with_updated_scores.dta", replace
    export delimited using ///
        "$OUT/EXACT_original_membership_2820_with_updated_scores.csv", replace
restore

preserve
    keep if psm_matched
    keep organization_name name_key vd_backed
    duplicates drop name_key vd_backed, force
    rename vd_backed new_treated
    save `NEW'
restore

use `OLD', clear
merge 1:1 name_key using `NEW'
gen byte old_control=old_treated==0 if !missing(old_treated)
gen byte new_control=new_treated==0 if !missing(new_treated)
gen byte old_treat=old_treated==1 if !missing(old_treated)
gen byte new_treat=new_treated==1 if !missing(new_treated)

tempname O
postfile `O' str48 statistic long value using "$OUT/original_overlap_summary.dta", replace
quietly count if old_control==1
post `O' ("Original matched controls") (r(N))
quietly count if new_control==1
post `O' ("Legacy-aligned rematched controls") (r(N))
quietly count if old_control==1 & new_control==1
post `O' ("Controls in both samples") (r(N))
quietly count if old_control==1 & new_control!=1
post `O' ("Original controls not retained") (r(N))
quietly count if new_control==1 & old_control!=1
post `O' ("Replacement controls") (r(N))
quietly count if old_treat==1 & new_treat==1
post `O' ("Treated firms in both samples") (r(N))
quietly count if old_treat==1 & new_treat!=1
post `O' ("Original treated not retained") (r(N))
quietly count if new_treat==1 & old_treat!=1
post `O' ("New treated not in original") (r(N))
postclose `O'

preserve
    keep if (old_control==1 & new_control!=1) | ///
        (new_control==1 & old_control!=1) | ///
        (old_treat==1 & new_treat!=1) | ///
        (new_treat==1 & old_treat!=1)
    keep organization_name name_key old_treated new_treated _merge
    export delimited using "$OUT/membership_differences.csv", replace
restore

use "$OUT/original_overlap_summary.dta", clear
export delimited using "$OUT/original_overlap_summary.csv", replace
list, noobs clean

log close
exit, clear
