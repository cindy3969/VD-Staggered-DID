* Tables 3-1 through 3-8: VD intensity and annual ultimately granted filings.
* Current Table 13 = legacy 3-1; Table 14 = legacy 3-4. Only these two run.
* Late = explicit Series C+; Seed/Angel/A/B = 0; unknown = missing.
* Created 2026-10-19. Reconstruction of specifications, NOT exact legacy results.
* Reference: VD Table 20260928.docx. 20260822 Table.docx has no Tables 3-1..3-8.
* Updated to include Table 3-8; filename/output directory retained for compatibility.
* Table 3-8 uses ln(cumulative VD USD), complete positive totals only.
* No user-written packages needed. Stata 18+.
* Run: do "C:/Users/user/Documents/VD/outputs/vd_intensity/replicate_tables_3_1_to_3_7.do"
version 18.0
clear all
set more off
capture log close vdint
local root "C:/Users/user/Documents/VD"
local out "`root'/outputs/vd_intensity/tables_3_1_to_3_7"
capture mkdir "`out'"
log using "`out'/replication.log", text replace name(vdint)

* SOURCE/DEFINITION CHOICES -- change here if original estimation code is recovered.
* Fixed doses: initial amount, ln(amount), two equity ratios, capital share,
* subsequent round count, ln(1+subsequent amount), ln(cumulative VD USD).
* Subsequent and cumulative measures use full source follow-up: descriptive, potentially endogenous
* and forward-looking. They are NOT annual realized exposure or causal dose effects.
* Prior patent and late stage moderators are fixed at the first VD year.
* Lagged controls: prior patent dummy, late stage dummy, ln(1+cumulative funding),
* ln(1+cumulative funding rounds). The original table does not establish +1 rules.
* Post includes the first VD calendar year. No event-window restriction imposed.
* Missing controls/moderators/dose are excluded, never replaced by zero here.
* Same complete-case sample across four columns WITHIN each table.
* Do not restrict firms to observed pre AND post years; audit that coverage only.
* All four columns use treated firms; columns 2/3 are interaction models, NOT subsets.
* Firm FE + year FE; standard errors clustered at firm level.

local doses vd_initial_usd ln_vd_initial vd_to_pre_equity vd_to_prev_equity vd_share_total_capital vd_subseq_rounds ln1p_vd_subseq ln_vd_cumulative
local firmfile "`root'/outputs/csdid_ultimately_granted_primary/csdid_ultimately_granted_full7316_controls.dta"
local panelfile "`root'/outputs/csdid_replicated_from_rebuilt_patent_list/csdid_rebuilt_patent_panel.dta"
confirm file "`firmfile'"
confirm file "`panelfile'"
use "`firmfile'", clear
isid organization_name
rename full_firm_id intensity_firm_id
rename first_vd_year intensity_vd_year
rename vd_backed intensity_treated
keep organization_name intensity_firm_id intensity_vd_year intensity_treated `doses' vd_earlier_debt_rounds
tempfile intensity
save `intensity'
use "`panelfile'", clear
isid full_firm_id year
* Match names, not potentially inconsistent IDs from independently rebuilt panels.
merge m:1 organization_name using `intensity', assert(match) nogen
assert full_firm_id==intensity_firm_id
assert vd_backed==intensity_treated
assert first_vd_year==intensity_vd_year if vd_backed==1
keep if vd_backed==1
assert first_vd_year<.
xtset full_firm_id year
assert apps_ult_granted>=0 if apps_ult_granted<.
generate double outcome=ln(1+apps_ult_granted)
generate byte post=year>=first_vd_year
generate byte prior=prior_patent_G
* Series classification from audited equity-round histories; original year-end timing retained.
preserve
use "`root'/outputs/csdid_all_applications_corrected/firm_year_all_applications_and_truncation_specs.dta", clear
keep organization_name year stage_endyear_text stage_preyear_text
duplicates drop
isid organization_name year
tempfile stages
save `stages'
restore
merge m:1 organization_name year using `stages', keep(master match) nogen
gen byte late_year=.
replace late_year=1 if regexm(lower(strtrim(stage_endyear_text)),"^series [c-z][0-9]*$")
replace late_year=0 if regexm(lower(strtrim(stage_endyear_text)),"^series [ab][0-9]*$") | inlist(lower(strtrim(stage_endyear_text)),"seed","pre-seed","angel")
gen byte late_at_G=late_year if year==first_vd_year
bysort full_firm_id: egen byte late=max(late_at_G)
drop late_at_G
xtset full_firm_id year
assert inlist(prior,0,1) if prior<.
assert inlist(late,0,1) if late<.
generate byte lag_late=.
replace lag_late=1 if regexm(lower(strtrim(stage_preyear_text)),"^series [c-z][0-9]*$")
replace lag_late=0 if regexm(lower(strtrim(stage_preyear_text)),"^series [ab][0-9]*$") | inlist(lower(strtrim(stage_preyear_text)),"seed","pre-seed","angel")
generate double ln1p_rounds_l1=ln(1+cum_funding_rounds_l1)
local controls prior_patent_l1 lag_late ln1p_cum_funding_l1 ln1p_rounds_l1
generate double post_prior=post*prior
generate double post_late=post*late
label variable outcome "Log(1 + ultimately granted applications by filing year)"
label variable post "Post"
label variable post_prior "Post x Prior patent"
label variable post_late "Post x Late stage"
label variable prior_patent_l1 "Lagged prior patent"
label variable lag_late "Lagged late stage"
label variable ln1p_cum_funding_l1 "Log(1 + lagged cumulative funding USD)"
label variable ln1p_rounds_l1 "Log(1 + lagged cumulative funding rounds)"
save "`out'/analysis_panel.dta", replace

* Machine-readable output: coefficients, cluster SEs, p-values, N, firms, within R2.
tempfile results samples
tempname coef sample
postfile `coef' int table model str40 term double b se p N firms within_r2 using `results', replace
postfile `sample' int table double firms_before firms_complete firms_both_periods using `samples', replace
local table=0
foreach dose of local doses {
    local ++table
    if !inlist(`table',1,4) continue
    preserve
    egen byte tag0=tag(full_firm_id)
    quietly count if tag0
    local before=r(N)
    generate byte complete=!missing(outcome,`dose',prior,late,post,prior_patent_l1,lag_late,ln1p_cum_funding_l1,ln1p_rounds_l1)
    keep if complete
    egen byte tag1=tag(full_firm_id)
    quietly count if tag1
    local complete_n=r(N)
    * Audit pre/post coverage without excluding post-only firms.
    bysort full_firm_id: egen byte minpost=min(post)
    bysort full_firm_id: egen byte maxpost=max(post)
    egen byte tag2=tag(full_firm_id)
    quietly count if tag2 & minpost==0 & maxpost==1
    local both=r(N)
    post `sample' (`table') (`before') (`complete_n') (`both')
    assert `complete_n'>1
    generate double dose_post=`dose'*post
    generate double dose_post_prior=dose_post*prior
    generate double dose_post_late=dose_post*late
    label variable dose_post "VD intensity x Post"
    label variable dose_post_prior "VD intensity x Post x Prior patent"
    label variable dose_post_late "VD intensity x Post x Late stage"
    forvalues m=1/4 {
        local rhs dose_post post `controls'
        if inlist(`m',2,4) local rhs `rhs' dose_post_prior post_prior
        if inlist(`m',3,4) local rhs `rhs' dose_post_late post_late
        * Fixed dose and moderator main effects absorbed by firm FE.
        * No dose x prior x late interaction is imposed by the reference tables.
        xtreg outcome `rhs' i.year, fe vce(cluster full_firm_id)
        estimates save "`out'/Table_3_`table'_model`m'.ster", replace
        foreach term of local rhs {
            scalar pv=.
            if _se[`term']>0 scalar pv=2*ttail(e(df_r),abs(_b[`term']/_se[`term']))
            post `coef' (`table') (`m') ("`term'") (_b[`term']) (_se[`term']) (pv) (e(N)) (e(N_g)) (e(r2_w))
        }
    }
    restore
}
postclose `coef'
postclose `sample'
use `samples', clear
export delimited using "`out'/sample_audit.csv", replace
use `results', clear
save "`out'/regression_results.dta", replace
export delimited using "`out'/regression_results_long.csv", replace

* Reporting tables: coefficient and p-value in parentheses; raw dollar coefficient
* keeps extra precision instead of displaying an economically opaque 0.000.
generate str50 cell=strtrim(string(b,"%12.6g"))
replace cell=cell+"***" if p<.01
replace cell=cell+"**" if p>=.01 & p<.05
replace cell=cell+"*" if p>=.05 & p<.10
replace cell=cell+" ("+strtrim(string(p,"%6.3f"))+")" if p<.
replace cell=cell+" [omitted]" if se==0
foreach t in 1 4 {
    preserve
    keep if table==`t'
    keep term model cell
    reshape wide cell, i(term) j(model)
    generate byte roworder=.
    local k=0
    foreach v in dose_post dose_post_prior dose_post_late post_prior post_late post prior_patent_l1 lag_late ln1p_cum_funding_l1 ln1p_rounds_l1 {
        local ++k
        replace roworder=`k' if term=="`v'"
    }
    sort roworder
    drop roworder
    rename (cell1 cell2 cell3 cell4) (Base Prior_interaction Late_interaction Both_interactions)
    export delimited using "`out'/Table_3_`t'.csv", replace
    restore
}
preserve
keep table model N firms within_r2
duplicates drop
sort table model
export delimited using "`out'/model_statistics.csv", replace
restore
display "Finished: Tables 13 and 14 (legacy 3-1 and 3-4), 4 specifications each; Series C+ late stage."
log close vdint

