version 19
clear all
set more off

global ROOT "C:/Users/user/Documents/VD/outputs/psm_final_2820_package"
capture mkdir "$ROOT/table3_original2820_full_results"
global OUT "C:/Users/user/Documents/VD/outputs/table_run_v2_20261020/table32_revision"

capture log close
log using "$OUT/RUN_TABLE3_FULL_v2.log", text replace
use "$ROOT/table3_original_2820_cross_section_v2.dta", clear

postfile capture_results int model str120 term double b se p N r2 F df fail kp using "$OUT/coefficients.dta", replace
program define capture_model
 syntax, ID(integer)
 tempname B V bb ss pp
 matrix `B'=e(b)
 matrix `V'=e(V)
 local names : colfullnames `B'
 forvalues j=1/`=colsof(`B')' {
  local term : word `j' of `names'
  scalar `bb'=`B'[1,`j']
  scalar `ss'=sqrt(`V'[`j',`j'])
  scalar `pp'=.
  if `ss'>0 & !missing(`ss') {
   if !missing(e(df_r)) & e(cmd)!="ppmlhdfe" scalar `pp'=2*ttail(e(df_r),abs(`bb'/`ss'))
   else scalar `pp'=2*normal(-abs(`bb'/`ss'))
  }
  post capture_results (`id') ("`term'") (`bb') (`ss') (`pp') (e(N)) (e(r2)) (e(F)) (e(df_r)) (e(N_fail)) (e(widstat))
 }
end

isid firm_id
assert _N==2820
* ORIGINAL2820_INNOVATION_REBUILT
display as text "Original 2820 firms. Innovation: complete reference+1..+3 windows through 2024."
tabulate innov_window_complete, missing
tabulate innovation_uncollected, missing
tabulate fog_win3_status, missing
tabulate novelty_status, missing
tabulate selftotal_status, missing
which reghdfe
which ivreghdfe
which esttab

* DV = ln(1 + number of patent applications filed in VD+1 through VD+3).
capture drop Priorpatent_VD
rename patentdummybyfiling Priorpatent_VD
capture drop Earlystage_VD
rename earlystage Earlystage_VD
capture drop ln_patentbyfiling_win3_2
gen ln_patentbyfiling_win3_2 = log(patentbyfiling_win3_2+1)
capture drop ln_priorpatent_VD_2
gen ln_priorpatent_VD_2 = log(priorpatent_VD_2+1)

capture drop priorpatentdummy_VD
* Regression moderator: 1 = prior patent; 0 = no prior patent.
gen priorpatentdummy_VD = Priorpatent_VD
capture drop nopriorpatentdummy_VD
gen nopriorpatentdummy_VD = 1 - priorpatentdummy_VD
label variable priorpatentdummy_VD "Prior patent at VD/reference year"
label variable nopriorpatentdummy_VD "No prior patent at VD/reference year"
capture drop ln_grantedbyfiling_win3
gen ln_grantedbyfiling_win3 = log(grantedpatentbyfiling_win3+1)
capture drop ln_grantedbyfiling_norm_win3
gen ln_grantedbyfiling_norm_win3 = log(grantedpatentbyfiling_norm_win3+1)

capture drop ln_norm_cite_perpat_win3_v1
gen ln_norm_cite_perpat_win3_v1 = log(norm_cite_perpat_win3_v1+1)
capture drop ln_norm_cite_perpat_win3_v2
gen ln_norm_cite_perpat_win3_v2 = log(norm_cite_perpat_win3_v2+1)
capture drop ln_norm_cite_perpat_win3_v3
gen ln_norm_cite_perpat_win3_v3 = log(norm_cite_perpat_win3_v3+1)
capture drop ln_norm_cite_perpat_win3_v4
gen ln_norm_cite_perpat_win3_v4 = log(norm_cite_perpat_win3_v4+1)
capture drop ln_norm_cite_perpat_win3_vv1
gen ln_norm_cite_perpat_win3_vv1 = log(norm_cite_perpat_win3_vv1+1)
capture drop ln_norm_cite_perpat_win3_vv2
gen ln_norm_cite_perpat_win3_vv2 = log(norm_cite_perpat_win3_vv2+1)
capture drop ln_norm_cite_perpat_win3_vv3
gen ln_norm_cite_perpat_win3_vv3 = log(norm_cite_perpat_win3_vv3+1)
capture drop ln_norm_cite_perpat_win3_vv4
gen ln_norm_cite_perpat_win3_vv4 = log(norm_cite_perpat_win3_vv4+1)

capture drop ln_moneyraised_win3
gen ln_moneyraised_win3 = log(moneyraised_win3+1)
capture drop ln_moneyraised_t1
gen ln_moneyraised_t1 = log(moneyraised_t1+1)
capture drop ln_moneyraised_t2
gen ln_moneyraised_t2 = log(moneyraised_t2+1)
capture drop ln_moneyraised_t3
gen ln_moneyraised_t3 = log(moneyraised_t3+1)

tab Industry2, gen(ind_)
tab Region2,   gen(reg_)

capture drop equityraised_win3
rename Follow_on_Equity_Raised_win3 equityraised_win3
capture drop ln_equityraised_win3
gen ln_equityraised_win3 = log(equityraised_win3+1)

* Industry: ind_1=Bio, ind_2=Hardware, ind_3=Other, ind_4=Software
label var ind_1 "Bio/Healthcare"
label var ind_2 "Hardware/Manufacturing/Deep Tech"
label var ind_4 "Software/IT services"

* Region: reg_1=California, reg_2=Massachusetts, reg_3=New York, reg_4=Other
label var reg_1 "California"
label var reg_2 "Massachusetts"
label var reg_3 "New York"

forvalues t = 1/3 {
capture drop ln_equityraised_t`t'
    gen ln_equityraised_t`t' = ln(1 + equityraised_t`t')
}

capture drop ma
rename m_a ma

capture drop ln_revenue_t1
gen ln_revenue_t1 = log(revenue_t1+1)
capture drop ln_revenue_t2
gen ln_revenue_t2 = log(revenue_t2+1)
capture drop ln_revenue_t3
gen ln_revenue_t3 = log(revenue_t3+1)

capture drop grantedbyfiling_norm_win3
rename grantedpatentbyfiling_norm_win3  grantedbyfiling_norm_win3 

capture drop ln_vdsupply
gen double ln_vdsupply = ln(1 + vdsupply)
capture drop ln_numberofvddeals
gen double ln_numberofvddeals = ln(1 + numberofvddeals)

capture drop ln_newpat_win3
gen ln_newpat_win3 = log(newpat_win3+1)
capture drop ln_oldpat_win3
gen ln_oldpat_win3 = log(oldpat_win3+1)

******************************ANALYSES*****************************
* Table1: Summary statistics
tabstat patent_application_win3 VD priorpatentdummy_VD Earlystage_VD MoneyRaised_VD NumofFundingRounds_VD ind_1 ind_2 ind_4 reg_1 reg_2 reg_3, ///
 statistics(N mean sd min max) columns(statistics)
 
* Table 2: Pairwise correlation
 pwcorr patent_application_win3 VD priorpatentdummy_VD Earlystage_VD MoneyRaised_VD NumofFundingRounds_VD ind_1 ind_2 ind_4 reg_1 reg_2 reg_3, sig star(.05)

local tablevars patent_application_win3 VD priorpatentdummy_VD Earlystage_VD MoneyRaised_VD NumofFundingRounds_VD ind_1 ind_2 ind_4 reg_1 reg_2 reg_3
tempname sm cr
postfile `sm' str40 variable double N mean sd min max using "$OUT/summary.dta", replace
foreach v of local tablevars {
 quietly summarize `v'
 post `sm' ("`v'") (r(N)) (r(mean)) (r(sd)) (r(min)) (r(max))
}
postclose `sm'
postfile `cr' str40 variable1 str40 variable2 double N r p using "$OUT/correlations.dta", replace
foreach v of local tablevars {
 foreach w of local tablevars {
  quietly correlate `v' `w'
  local n=r(N)
  local rho=r(rho)
  local p=.
  if abs(`rho')<1 local p=2*ttail(`n'-2,abs(`rho')*sqrt((`n'-2)/(1-`rho'^2)))
  post `cr' ("`v'") ("`w'") (`n') (`rho') (`p')
 }
}
postclose `cr'



* Table 3-2: Funding-stage heterogeneity (cross-sectional three-year window)
* Existing stage assignments include imputations; see stage_method.
preserve
use "C:/Users/user/Documents/VD/260122 winsorization_stage4.dta", clear
keep firm_id OrganizationName VD VDyear stage4 stage_inference_method
rename OrganizationName stage_name
rename VD stage_vd
rename VDyear stage_year
rename stage4 fundstage
rename stage_inference_method stage_method
tempfile funding_stages
save `funding_stages'
restore
merge 1:1 firm_id using `funding_stages', generate(stage_merge)
assert stage_merge == 3
assert OrganizationName == stage_name & VD == stage_vd & VDyear == stage_year
drop stage_merge stage_name stage_vd stage_year
label variable fundstage "Funding stage at initial VD date or control reference year"
label define fundstage_lbl 1 "Seed / pre-Series" 2 "Series A" 3 "Series B" 4 "Series C+", replace
label values fundstage fundstage_lbl
label variable stage_method "Reference-stage assignment method, including imputation"
notes fundstage: Highest prior Series; otherwise future-round backcast or round-order fallback.
notes fundstage: One grant-only firm was assumed Seed in source. Not an observed Series.
gen byte early_sb = inrange(fundstage,1,3) if !missing(fundstage)
label variable early_sb "1=Seed through Series B; 0=Series C+ at reference point"
tab fundstage VD, row

* Panel B: stage-specific VD effects, using the current Table 3 outcome and FE.
reghdfe ln_grantedbyfiling_norm_win3 i.VD ib1.fundstage ///
    i.priorpatentdummy_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
capture_model, id(1)
estimates store T32_stage
margins fundstage, dydx(1.VD) predict(xb) post
capture_model, id(2)

reghdfe ln_grantedbyfiling_norm_win3 i.VD##i.priorpatentdummy_VD ib1.fundstage ///
     ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
capture_model, id(3)
estimates store T32_stage
margins fundstage, dydx(1.VD) predict(xb) post
capture_model, id(4)

reghdfe ln_grantedbyfiling_norm_win3 i.VD##ib1.fundstage ///
    i.priorpatentdummy_VD  ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
capture_model, id(5)
estimates store T32_full
lincom 1.VD#4.fundstage - 1.VD#3.fundstage
margins fundstage, dydx(1.VD) predict(xb) post
capture_model, id(6)
***
reghdfe ln_grantedbyfiling_norm_win3 i.VD##ib1.fundstage ///
   i.VD##i.priorpatentdummy_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
capture_model, id(7)
estimates store T32_full
lincom 1.VD#4.fundstage - 1.VD#3.fundstage
margins fundstage, dydx(1.VD) predict(xb) post
capture_model, id(8)

postclose capture_results
display "TABLE32_COMPLETE"
log close
