* Called by RUN_TABLE3_PATENT_APPLICATION_WIN3.do; also runnable alone.
* Preserves caller data. All outcomes use filing years t+1..t+3.
* New-domain results are conditional on a complete, nonempty pre-t portfolio.
* Primary CPC3 novelty != novel recombination. Partner distance != own distance.
* Citation cutoff is 2024-12-31. No unavailable values are zero-filled here.
version 19
preserve
global INROOT "C:/Users/user/Documents/VD/outputs/psm_final_2820_package"
capture mkdir "$INROOT/table3_application_results"
global INOUT "$INROOT/table3_application_results/innovation"
capture mkdir "$INOUT"
capture log close innovation
log using "$INOUT/innovation_win3.log", text replace name(innovation)
use "$INROOT/table3_current_2820_cross_section_v2.dta", clear
isid firm_id
gen byte no_prior = 1-priorpatentdummy_VD
gen byte early = earlystage
local controls "i.no_prior i.early c.ln_MoneyRaised_VD c.NumofFundingRounds_VD"
local fe "i.Region2 i.Industry2 i.Foundingyear"
* New-domain baseline: all matched own patents granted before reference-year
* Jan 1. newpat/oldpat partition primary CPC3 relative to that FIXED set.
* No baseline -> missing, not new-domain=1. Counts include post-patent zeros;
* shares and distances condition on at least one classified post patent.
* own_dist = mean[1-cosine(one-hot primary CPC3, baseline class distribution)].
* selfshare pools backward self-citations / all backward patent citations.
* Explicit FE indicators implement the Table 3 FE structure with built-in
* regress/fracreg/poisson; no singleton pruning or add-on installation needed.
* No post-VD fundraising, employment or patent-count controls in primary fits.

* Existing Table A7 readability/figures/sheets/claims/grant-rate block is
* intentionally untouched and NOT repeated by this module.
local fractions "nocite_win3 breakthrough_win3 originality_win3 generality_win3 cite_diversity_win3 newshare_win3 own_dist_win3 selfshare_win3"
local levels "partner_search_win3"
local skew "desc_words_win3 cite_breadth_win3 selfcite_win3 partner_dist_win3"
local counts "newpat_win3 oldpat_win3 newcpc_win3"
local all "`fractions' `levels' `skew' `counts'"
tempname res
postfile `res' str32 dv str24 model double N N_VD N_control b se p lo hi ///
    int rc using "$INOUT/innovation_models.dta", replace

foreach y of local all {
    confirm numeric variable `y'
    local transform : list y in skew
    local iscount : list y in counts
    local fraction : list y in fractions
    capture drop outcome available
    gen double outcome = `y'
    if `transform' | `iscount' {
        assert `y'>=0 if !missing(`y')
        replace outcome = ln(1+`y')
    }
    if `fraction' assert inrange(`y',0,1) if !missing(`y')
    gen byte available = win3_observed==1 & !missing(outcome,VD,no_prior,early,ln_MoneyRaised_VD, ///
        NumofFundingRounds_VD,Region2,Industry2,Foundingyear)
    quietly count if available & VD==1
    local nt=r(N)
    quietly count if available & VD==0
    local nc=r(N)
    di as text "DV `y': treated=`nt', control=`nc'; ln1p=`transform' or `iscount'"
    * First four specifications parallel main Table 3. Fifth adds reference-
    * year FE as a cohort/citation-exposure robustness check (not equal horizons).
    forvalues spec=1/5 {
        local rhs "i.VD `controls' `fe'"
        if `spec'==2 local rhs "i.VD##i.no_prior i.early c.ln_MoneyRaised_VD c.NumofFundingRounds_VD `fe'"
        if `spec'==3 local rhs "i.VD##i.early i.no_prior c.ln_MoneyRaised_VD c.NumofFundingRounds_VD `fe'"
        if `spec'==4 local rhs "i.VD##i.no_prior i.VD##i.early c.ln_MoneyRaised_VD c.NumofFundingRounds_VD `fe'"
        if `spec'==5 local rhs "i.VD `controls' `fe' i.VDyear"
        capture noisily regress outcome `rhs' if available, vce(robust)
        local err=_rc
        if `err'==0 {
            estimates save "$INOUT/`y'_ols`spec'.ster", replace
            * For interacted models report average discrete VD change, not
            * merely the VD coefficient for the omitted moderator category.
            capture noisily margins, dydx(VD)
            local err=_rc
            if `err'==0 {
                matrix M=r(table)
                local j=colnumb("M","1.VD")
                if missing(`j') local err=498
                else if missing(M[1,`j'],M[2,`j'],M[4,`j']) local err=498
                if `err'==0 post `res' ("`y'") ("ols`spec'_VD_AME") (e(N)) (`nt') (`nc') ///
                    (M[1,`j']) (M[2,`j']) (M[4,`j']) (M[5,`j']) (M[6,`j']) (0)
            }
            if `spec'==2 | `spec'==4 capture noisily test 1.VD#1.no_prior
            if `spec'==3 | `spec'==4 capture noisily test 1.VD#1.early
        }
        if `err'!=0 post `res' ("`y'") ("ols`spec'_VD_AME") (.) (`nt') (`nc') (.) (.) (.) (.) (.) (`err')
    }
    * Functional-form checks: fractional logit keeps 0 and 1 observations;
    * count PPML includes zero counts. Report AMEs on original outcome scale.
    if `fraction' | `iscount' {
        local family "fraclogit"
        if `fraction' capture noisily fracreg logit `y' i.VD `controls' `fe' if available, vce(robust) iterate(100)
        if `iscount' {
            local family "poisson"
            capture noisily poisson `y' i.VD `controls' `fe' if available, vce(robust) iterate(100)
        }
        local err=_rc
        if `err'==0 {
            if e(converged)!=1 local err=430
        }
        if `err'==0 {
            estimates save "$INOUT/`y'_`family'.ster", replace
            quietly count if e(sample) & VD==1
            local nt2=r(N)
            quietly count if e(sample) & VD==0
            local nc2=r(N)
            capture noisily margins, dydx(VD)
            local err=_rc
            if `err'==0 {
                matrix M=r(table)
                local j=colnumb("M","1.VD")
                if missing(`j') local err=498
                else if missing(M[1,`j'],M[2,`j'],M[4,`j']) local err=498
                if `err'==0 post `res' ("`y'") ("`family'_VD_AME") (e(N)) (`nt2') (`nc2') ///
                    (M[1,`j']) (M[2,`j']) (M[4,`j']) (M[5,`j']) (M[6,`j']) (0)
            }
        }
        if `err'!=0 post `res' ("`y'") ("`family'_VD_AME") (.) (`nt') (`nc') (.) (.) (.) (.) (.) (`err')
    }
}

* DIRECT HYPOTHESIS: VD is more negatively associated with new-domain
* development than with existing-domain development. A significant result in
* one equation and an insignificant result in the other is NOT this test.
* Same firms, same baseline, same grant observation cutoff in both equations.
keep if win3_observed==1 & !missing(newpat_win3,oldpat_win3,VD,no_prior,early,ln_MoneyRaised_VD, ///
    NumofFundingRounds_VD,Region2,Industry2,Foundingyear)
gen double log_new_old = ln(1+newpat_win3)-ln(1+oldpat_win3)
regress log_new_old i.VD `controls' `fe', vce(robust)
estimates save "$INOUT/new_vs_old_log_difference.ster", replace
lincom 1.VD
post `res' ("new_minus_old") ("log1p_diff_VD") (e(N)) (.) (.) ///
    (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (0)

* Stacked PPML: all covariate effects differ by domain; cluster by firm.
* Interaction is the log ratio of the two VD incidence-rate ratios.
expand 2
bysort firm_id: gen byte newdomain = _n-1
gen double domain_patents = cond(newdomain==1,newpat_win3,oldpat_win3)
capture noisily poisson domain_patents i.newdomain##(i.VD `controls' `fe'), ///
    vce(cluster firm_id) iterate(100)
local err=_rc
if `err'==0 {
    if e(converged)!=1 local err=430
}
if `err'==0 {
    estimates save "$INOUT/new_vs_old_stacked_ppml.ster", replace
    lincom 1.newdomain#1.VD
    post `res' ("new_minus_old") ("PPML_log_IRR_difference") (e(N)/2) (.) (.) ///
        (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (0)
    test 1.newdomain#1.VD
}
if `err'!=0 post `res' ("new_minus_old") ("PPML_log_IRR_difference") (.) (.) (.) (.) (.) (.) (.) (.) (`err')
postclose `res'
use "$INOUT/innovation_models.dta", clear
label var b "VD average discrete change; differential tests as model name"
label var p "Two-sided p-value, unadjusted"
label var rc "0=completed; nonzero=estimation/margins failure, not a null result"
gen str32 outcome_scale = "original DV units"
foreach y of local skew {
    replace outcome_scale="ln(1+DV) units" if dv=="`y'" & substr(model,1,3)=="ols"
}
foreach y of local counts {
    replace outcome_scale="ln(1+DV) units" if dv=="`y'" & substr(model,1,3)=="ols"
}
replace outcome_scale="log ratio of VD IRRs" if model=="PPML_log_IRR_difference"
replace outcome_scale="ln(1+new)-ln(1+old)" if model=="log1p_diff_VD"
* Exploratory multiple-DV control: BH q-values for baseline OLS only.
gen byte bh_family = model=="ols1_VD_AME" & rc==0 & !missing(p)
gsort -bh_family p
quietly count if bh_family
local m=r(N)
gen double q_bh = min(1,p*`m'/_n) if bh_family
if `m'>1 {
    local start=`m'-1
    forvalues j=`start'(-1)1 {
        replace q_bh=min(q_bh,q_bh[`j'+1]) in `j'
    }
}
label var q_bh "Benjamini-Hochberg q: baseline OLS across all innovation DVs"
sort dv model
save "$INOUT/innovation_models.dta", replace
export delimited using "$INOUT/innovation_models.csv", replace
list dv model N b p rc if dv=="new_minus_old", noobs abbreviate(24)
count if rc!=0
di as text "Models with recorded estimation/margins failures: " r(N)
log close innovation
restore
