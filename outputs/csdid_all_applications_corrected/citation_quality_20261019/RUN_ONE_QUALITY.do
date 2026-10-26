version 19
args version
clear all
set more off
set linesize 255
global P "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected"
global Q "$P/citation_quality_20261019"
capture log close _all
log using "$Q/quality_v`version'.log", text replace
use "$P/firm_year_all_applications_and_truncation_specs.dta", clear
local dv norm_cite_perpat_v`version'
keep if year<=2024
drop if missing(`dv',ln1p_cum_funding_l1,cum_funding_rounds_l1,region_fe,industry_fe,full_firm_id,year,G)
tempname H
postfile `H' str12 sample str12 control str12 aggregation str40 effect double att se p N firms int rc using "$Q/quality_v`version'_results.dta", replace
foreach sample in all noprior prior early late notyet {
    local condition "1"
    local opt ""
    local ctrl "never"
    if "`sample'"=="noprior" local condition "G==0 | prior==0"
    if "`sample'"=="prior" local condition "G==0 | prior==1"
    if "`sample'"=="early" local condition "G==0 | early==1"
    if "`sample'"=="late" local condition "G==0 | early==0"
    if "`sample'"=="notyet" {
        local opt "notyet"
        local ctrl "notyet"
    }
    quietly count if `condition'
    local N=r(N)
    egen byte tag=tag(full_firm_id) if `condition'
    quietly count if tag==1
    local firms=r(N)
    drop tag
    display "BEGIN_SPEC v`version' `sample' N=`N' firms=`firms'"
    capture noisily csdid `dv' ln1p_cum_funding_l1 cum_funding_rounds_l1 i.region_fe i.industry_fe if `condition', ivar(full_firm_id) time(year) gvar(G) method(dripw) `opt'
    local rc=_rc
    if `rc' {
        post `H' ("`sample'") ("`ctrl'") ("failed") ("csdid") (.) (.) (.) (`N') (`firms') (`rc')
        continue
    }
    foreach agg in simple event group {
        local window ""
        if "`agg'"=="event" local window ", window(-4 4)"
        capture noisily csdid_estat `agg' `window'
        local rc=_rc
        if `rc' {
            post `H' ("`sample'") ("`ctrl'") ("`agg'") ("failed") (.) (.) (.) (`N') (`firms') (`rc')
            continue
        }
        matrix T=r(table)
        local names: colnames T
        local j=0
        foreach term of local names {
            local ++j
            post `H' ("`sample'") ("`ctrl'") ("`agg'") ("`term'") (T[1,`j']) (T[2,`j']) (T[4,`j']) (`N') (`firms') (0)
        }
    }
    display "END_SPEC v`version' `sample'"
}
postclose `H'
use "$Q/quality_v`version'_results.dta", clear
export delimited using "$Q/quality_v`version'_results.csv", replace
log close
