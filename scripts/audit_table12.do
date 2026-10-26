version 19
clear all
set more off
set linesize 255
capture log close _all
log using "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected/Table12_audit.log", text replace
which csdid
use "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected/firm_year_all_applications_and_truncation_specs.dta", clear
keep if year<=2024
drop if missing(grantedapp_norm, ln1p_cum_funding_l1, cum_funding_rounds_l1, region_fe, industry_fe, full_firm_id, year, G)
count
egen byte audit_tag=tag(full_firm_id)
count if audit_tag==1
drop audit_tag
display "AUDIT: RAW NORMALIZED DV, NEVER-TREATED"
quietly csdid grantedapp_norm ln1p_cum_funding_l1 cum_funding_rounds_l1 i.region_fe i.industry_fe, ivar(full_firm_id) time(year) gvar(G) method(dripw)
csdid_estat simple
csdid_estat event, window(-4 4)
csdid_estat group
display "AUDIT: RAW NORMALIZED DV, NOT-YET-TREATED"
quietly csdid grantedapp_norm ln1p_cum_funding_l1 cum_funding_rounds_l1 i.region_fe i.industry_fe, ivar(full_firm_id) time(year) gvar(G) method(dripw) notyet
csdid_estat simple
csdid_estat event, window(-4 4)
csdid_estat group
display "AUDIT COMPLETE"
log close
exit, clear
