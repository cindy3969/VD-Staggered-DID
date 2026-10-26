version 19
clear all
set more off

global ROOT "C:/Users/user/Documents/VD/outputs/psm_final_2820_package"
capture mkdir "$ROOT/table3_original2820_full_results"
global OUT "$ROOT/table3_original2820_full_results"

capture log close
log using "$OUT/RUN_TABLE3_FULL_v2.log", text replace
use "$ROOT/table3_original_2820_cross_section_v2.dta", clear
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

capture drop ln_patentbyfiling_win3_2
gen ln_patentbyfiling_win3_2 = log(patentbyfiling_win3_2+1)
capture drop ln_priorpatent_VD_2
gen ln_priorpatent_VD_2 = log(priorpatent_VD_2+1)

* Regression moderator: 1 = prior patent; 0 = no prior patent.

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

* for Table 3-2: Funding-stage heterogeneity (cross-sectional three-year window)
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
save "$OUT/table3_2_analysis.dta", replace

*gen latestage_VD = (fundstage == 4) if !missing(fundstage)
*label variable latestage_VD "Series C+ at VD/reference date"

tab latestage_VD, missing

*******************************************************************
******************************ANALYSES*****************************
* Table1: Summary statistics
tabstat patent_application_win3 VD priorpatentdummy_VD latestage_VD MoneyRaised_VD NumofFundingRounds_VD ind_1 ind_2 ind_4 reg_1 reg_2 reg_3, ///
 statistics(N mean sd min max) columns(statistics)
 
* Table 2: Pairwise correlation
 pwcorr patent_application_win3 VD priorpatentdummy_VD latestage_VD MoneyRaised_VD NumofFundingRounds_VD ind_1 ind_2 ind_4 reg_1 reg_2 reg_3, sig star(.05)

* Table 3: Patent quantity
reghdfe ln_grantedbyfiling_norm_win3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel

reghdfe ln_grantedbyfiling_norm_win3 i.VD##i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel

reghdfe ln_grantedbyfiling_norm_win3 priorpatentdummy_VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel

reghdfe ln_grantedbyfiling_norm_win3 i.VD##i.priorpatentdummy_VD ///
    i.VD##i.latestage_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel

*Table 4-1 and 4-2
reghdfe ln_grantedbyfiling_norm_win3 i.VD ib1.fundstage ///
    i.priorpatentdummy_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
margins fundstage, dydx(1.VD) predict(xb) post

reghdfe ln_grantedbyfiling_norm_win3 i.VD##i.priorpatentdummy_VD ib1.fundstage ///
     ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
margins fundstage, dydx(1.VD) predict(xb) post

reghdfe ln_grantedbyfiling_norm_win3 i.VD##ib1.fundstage ///
    i.priorpatentdummy_VD  ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
margins fundstage, dydx(1.VD) predict(xb) post

reghdfe ln_grantedbyfiling_norm_win3 i.VD##ib1.fundstage ///
   i.VD##i.priorpatentdummy_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
margins fundstage, dydx(1.VD) predict(xb) post

* Table 5: Patent quality
reghdfe ln_norm_cite_perpat_win3_v4 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel

reghdfe ln_norm_cite_perpat_win3_v4 i.VD##i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel

reghdfe ln_norm_cite_perpat_win3_v4 i.priorpatentdummy_VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel

reghdfe ln_norm_cite_perpat_win3_v4 i.VD##i.priorpatentdummy_VD ///
    i.VD##i.latestage_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel


* Table 6: follow on equity raised 
reghdfe ln_moneyraised_win3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel

reghdfe ln_moneyraised_win3 i.VD##i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel

reghdfe ln_moneyraised_win3 i.priorpatentdummy_VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel

reghdfe ln_moneyraised_win3 i.VD##i.priorpatentdummy_VD ///
    i.VD##i.latestage_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel


* Table 7
forvalues h=1/3 {
    reghdfe ln_moneyraised_y`h' VD i.priorpatentdummy_VD i.latestage_VD ///
        ln_MoneyRaised_VD NumofFundingRounds_VD, ///
        absorb(Region2 Industry2 Foundingyear) vce(robust)
    estimates store legacy6_`h'
}

* Table 8
local j = 0

foreach event in acq3 public3 badexit3 {
    stset VDage3, failure(`event'==1) id(firm_id)

    stcox VD i.Region2 i.Industry2 i.Foundingyear, nohr
    local ++j
    estimates store legacy7_`j'

    stcox VD priorpatentdummy_VD latestage_VD ln_MoneyRaised_VD ///
        NumofFundingRounds_VD i.Region2 i.Industry2 i.Foundingyear, nohr
    local ++j
    estimates store legacy7_`j'
}





*******************APPENDIX********************
* Table A1: IV 2SLS
* (1) Second stage: 2SLS
ivreghdfe ln_grantedbyfiling_norm_win3 ///
    priorpatentdummy_VD latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    (VD = ln_vdsupply), ///
    absorb(Region2 Industry2 Foundingyear) robust first

estimates store IV_second
gen byte iv_sample = e(sample)

scalar CD_F = e(cdf)
scalar KP_F = e(widstat)

* (2) First stage: 동일한 추정 표본 사용
reghdfe VD ln_vdsupply ///
    priorpatentdummy_VD latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    if iv_sample == 1, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)

test ln_vdsupply
scalar excluded_IV_F = r(F)
estimates store IV_first


* Table A2: patenting firms only
reghdfe ln_grantedbyfiling_norm_win3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    if grantedbyfiling_norm_win3 > 0 & !missing(grantedbyfiling_norm_win3), ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results_positive.xls, replace dec(3) pvalue excel

reghdfe ln_grantedbyfiling_norm_win3 i.VD##i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    if grantedbyfiling_norm_win3 > 0 & !missing(grantedbyfiling_norm_win3), ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results_positive.xls, append dec(3) pvalue excel

reghdfe ln_grantedbyfiling_norm_win3 priorpatentdummy_VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    if grantedbyfiling_norm_win3 > 0 & !missing(grantedbyfiling_norm_win3), ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results_positive.xls, append dec(3) pvalue excel

reghdfe ln_grantedbyfiling_norm_win3 i.VD##i.priorpatentdummy_VD ///
    i.VD##i.latestage_VD ln_MoneyRaised_VD NumofFundingRounds_VD ///
    if grantedbyfiling_norm_win3 > 0 & !missing(grantedbyfiling_norm_win3), ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results_positive.xls, append dec(3) pvalue excel


*Table A3
isid firm_id

* 필수 변수 확인
confirm variable VD priorpatentdummy_VD latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    Region2 Industry2 Foundingyear VDyear ///
    raise1 raise2 raise3 complete1 complete2 complete3 ///
    cum1 cum2 cum3 undisclosed1 undisclosed2 undisclosed3 ///
    duration_days observed next_event next_days next_amount next_n

*A3 Panle A
assert missing(raise1) if complete1 == 0
assert missing(raise2) if complete2 == 0
assert missing(raise3) if complete3 == 0

reghdfe raise1 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)

reghdfe raise2 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)

reghdfe raise3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)

* A3 Panel B
capture drop stop3 surv_days event3 surv_event ln_next_amount

gen double stop3 = mdy(12,31,VDyear+3) - mdy(12,31,VDyear)

gen byte event3 = (next_event == 1 & next_days <= stop3) ///
    if observed == 1 & !missing(next_event, stop3)
replace event3 = . if observed == 1 & next_event == 1 ///
    & missing(next_days)

gen double surv_days = min(duration_days,1095) ///
    if observed == 1 & !missing(duration_days)

gen byte surv_event = (next_event == 1 & next_days <= 1095) ///
    if observed == 1 & !missing(next_event)
replace surv_event = . if observed == 1 & next_event == 1 ///
    & missing(next_days)

stset surv_days if observed == 1 & !missing(surv_event), ///
    failure(surv_event == 1) id(firm_id)

* (1) Cox model: log-hazard coefficients
stcox VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear, ///
    nohr vce(robust)
* (2) Weibull AFT model: log-time coefficients
streg VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear, ///
    distribution(weibull) time nohr vce(robust)
* (3) Next-round amount, conditional on raising within 3 years
gen double ln_next_amount = ln(next_amount) ///
    if next_amount > 0 & !missing(next_amount)

reghdfe ln_next_amount ///
    VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    if complete3 == 1 & event3 == 1 & next_n == 1, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)

* A3 Panel C

assert missing(cum1) if undisclosed1 == 1
assert missing(cum2) if undisclosed2 == 1
assert missing(cum3) if undisclosed3 == 1

capture drop ln_cum_usd1 ln_cum_usd2 ln_cum_usd3

gen double ln_cum_usd1 = ln(1 + cum1)
gen double ln_cum_usd2 = ln(1 + cum2)
gen double ln_cum_usd3 = ln(1 + cum3)

reghdfe ln_cum_usd1 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)

reghdfe ln_cum_usd2 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)

reghdfe ln_cum_usd3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)


* Table A4: Employee
regress emp2025_2 VD i.lastdeal2vd1 ///
    if private==1 & inrange(lastdeal2vd1,1,3), vce(robust)

regress emp2025_2 VD patentdummybyfiling latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.lastdeal2vd1 i.Founding_Year ib4.Region2 ib3.Industry2 ///
    if private==1 & inrange(lastdeal2vd1,1,3), vce(robust)

regress emp2025_2 i.VD##ib0.patentdummybyfiling latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.lastdeal2vd1 i.Founding_Year ib4.Region2 ib3.Industry2 ///
    if private==1 & inrange(lastdeal2vd1,1,3), vce(robust)

regress emp2025_2 patentdummybyfiling i.VD##ib0.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.lastdeal2vd1 i.Founding_Year ib4.Region2 ib3.Industry2 ///
    if private==1 & inrange(lastdeal2vd1,1,3), vce(robust)

regress emp2025_2 i.VD##ib0.patentdummybyfiling i.VD##ib0.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.lastdeal2vd1 i.Founding_Year ib4.Region2 ib3.Industry2 ///
    if private==1 & inrange(lastdeal2vd1,1,3), vce(robust)

***Other innovation measures
*tatstast nocite_win3 breakthrough_win3 claims_win3 gunning_fog_win3 ari_win3 oldpat_win3 newcpc_win3 cite_breadth_win3 selfcite_win3, ///
 statistics(N mean sd min max) columns(statistics)

*sum nocite_win3 breakthrough_win3 desc_words_win3 fog_win3 ari_win3 neg_flesch_win3 figures_win3 sheets_win3 claims_win3

capture drop ln_desc_words_win3
gen ln_desc_words_win3 = log(desc_words_win3+1)
capture drop ln_figures_win3
gen ln_figures_win3 = log(figures_win3+1)
capture drop ln_sheets_win3
gen ln_sheets_win3 = log(sheets_win3+1)
capture drop ln_claims_win3
gen ln_claims_win3 = log(claims_win3+1)


*fracreg logit nocite_win3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear, vce(robust)
*fracreg logit nocite_win3 i.VD##i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear, vce(robust)
*fracreg logit nocite_win3 i.priorpatentdummy_VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear, vce(robust)
*fracreg logit nocite_win3 i.VD##i.priorpatentdummy_VD  i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear, vce(robust)


*reghdfe breakthrough_win3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
*reghdfe breakthrough_win3  i.VD##i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
*reghdfe breakthrough_win3  i.priorpatentdummy_VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
*reghdfe breakthrough_win3  i.VD##i.priorpatentdummy_VD ///
    i.VD##i.latestage_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)


*reghdfe ln_claims_win3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
*reghdfe ln_claims_win3 i.VD##i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
*reghdfe ln_claims_win3 i.priorpatentdummy_VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
*reghdfe ln_claims_win3 i.VD##i.priorpatentdummy_VD ///
    i.VD##i.latestage_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
	
* Table A7: patent readability
reghdfe gunning_fog_win3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
reghdfe gunning_fog_win3 i.VD##i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
reghdfe gunning_fog_win3 i.priorpatentdummy_VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
reghdfe gunning_fog_win3 i.VD##i.priorpatentdummy_VD ///
    i.VD##i.latestage_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)


* Table A8
reghdfe ari_win3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
reghdfe ari_win3 i.VD##i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
reghdfe ari_win3 i.priorpatentdummy_VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
reghdfe ari_win3 i.VD##i.priorpatentdummy_VD ///
    i.VD##i.latestage_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)

	
* Table A9
reghdfe neg_flesch_win3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
reghdfe neg_flesch_win3 i.VD##i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
reghdfe neg_flesch_win3 i.priorpatentdummy_VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
reghdfe neg_flesch_win3 i.VD##i.priorpatentdummy_VD ///
    i.VD##i.latestage_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)

* Table A10
reghdfe ln_newpat_win3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)

reghdfe ln_newpat_win3 i.VD##i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)

reghdfe ln_newpat_win3 priorpatentdummy_VD VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)

reghdfe ln_newpat_win3 VD i.VD##i.priorpatentdummy_VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)


* Table A11
ppmlhdfe ln_oldpat_win3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
ppmlhdfe ln_oldpat_win3 i.VD##i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
ppmlhdfe ln_oldpat_win3 priorpatentdummy_VD VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
ppmlhdfe ln_oldpat_win3 VD i.VD##i.priorpatentdummy_VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)


* Table A12
ppmlhdfe newcpc_win3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
ppmlhdfe newcpc_win3 i.VD##i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
ppmlhdfe newcpc_win3 priorpatentdummy_VD VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
ppmlhdfe newcpc_win3 VD i.VD##i.priorpatentdummy_VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)



* Table A13
reghdfe cite_breadth_win3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
reghdfe cite_breadth_win3 i.VD##i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
reghdfe cite_breadth_win3 priorpatentdummy_VD VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
reghdfe cite_breadth_win3 VD i.VD##i.priorpatentdummy_VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
	
* Table A14
ppmlhdfe selfcite_win3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
ppmlhdfe selfcite_win3 i.VD##i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
ppmlhdfe selfcite_win3 priorpatentdummy_VD VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
ppmlhdfe selfcite_win3 VD i.VD##i.priorpatentdummy_VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)




*tabstat  nocite_win3 breakthrough_win3 desc_words_win3 fog_win3 ari_win3 ///
    neg_flesch_win3 figures_win3 sheets_win3 claims_win3 newpat_win3 oldpat_win3 ///
    newcpc_win3 cite_breadth_win3 self_citations_total_win3	fog_win3 ari_win3 neg_flesch_win3 	originality_win3 cite_diversity_win3 cite_breadth_win3 selfcite_win3 self_citations_total_win3 selfcite__win3 selfshare_win3 generality_win3, ///
 statistics(N mean sd min max) columns(statistics)


