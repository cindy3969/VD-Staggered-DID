version 19
clear all
set more off
set linesize 255
capture log close _all
log using "C:/Users/user/Documents/VD/outputs/refresh_did_20261023/grantedapp_norm_prior.log", text replace
capture program drop construct_late
program define construct_late
    confirm variable full_firm_id year G stage_preyear_text
    capture drop late
    capture drop late_at_G
    capture drop stage_at_G
    gen str244 stage_at_G = lower(strtrim(stage_preyear_text)) if G>0 & year==G
    gen byte late_at_G = .
    replace late_at_G = 1 if G>0 & year==G & regexm(stage_at_G,"^series [c-z][0-9]*$")
    replace late_at_G = 0 if G>0 & year==G & ///
        (regexm(stage_at_G,"^series [ab][0-9]*$") | inlist(stage_at_G,"seed","pre-seed","angel"))
    bysort full_firm_id: egen byte late = max(late_at_G)
    label variable late "Series C+ through G-1 (1); Seed through B (0); unknown missing"
    label define late_stage_label 0 "Seed through Series B" 1 "Series C+", replace
    label values late late_stage_label
    drop late_at_G stage_at_G
end


global P "C:/Users/user/Documents/VD/outputs/csdid_all_applications_corrected"
global Q "C:/Users/user/Documents/VD/outputs/refresh_did_20261023"
use "$P/firm_year_all_applications_and_truncation_specs.dta", clear
construct_late
local dv grantedapp_norm
keep if year<=2024
drop if missing(`dv',ln1p_cum_funding_l1,cum_funding_rounds_l1,region_fe,industry_fe,full_firm_id,year,G)
tempname H
postfile `H' str12 sample str12 control str12 aggregation str40 effect double att se p N firms int rc using "$Q/grantedapp_norm_prior_results.dta", replace
foreach sample in prior {
    local condition "1"
    local opt ""
    local ctrl "never"
    if "`sample'"=="noprior" local condition "G==0 | prior==0"
    if "`sample'"=="prior" local condition "G==0 | prior==1"
    if "`sample'"=="nonlate" local condition "G==0 | late==0"
    if "`sample'"=="late" local condition "G==0 | late==1"
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
    display "BEGIN_SPEC v4 `sample' N=`N' firms=`firms'"
    capture quietly csdid `dv' ln1p_cum_funding_l1 cum_funding_rounds_l1 i.region_fe i.industry_fe if `condition', ivar(full_firm_id) time(year) gvar(G) method(dripw) `opt'
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
    display "END_SPEC v4 `sample'"
}
postclose `H'
use "$Q/grantedapp_norm_prior_results.dta", clear
assert rc==0
display "REQUESTED_DID_COMPLETE"
log close
