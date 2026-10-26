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
esttab legacy7_1 legacy7_2 legacy7_3 legacy7_4 legacy7_5 legacy7_6 ///
    using "$OUT/Table7_legacy_replication.csv", replace b(6) se(6) stats(N N_fail)
restore

* Four supporting estimands; separate outputs, no changes to innovation outcomes.
* Financing support analysis embedded directly in this master do-file.
* Supporting evidence, not a mediation test. Post-treatment selection affects amounts.
* Build data with scripts/build_downstream_financing.py after updating source/cutoff.
preserve
local D "C:/Users/user/Documents/VD/outputs/downstream_financing"
* 후속 금융성과 변수를 현재 데이터에 추가
isid firm_id

merge 1:1 firm_id using ///
    "C:/Users/user/Documents/VD/outputs/downstream_financing/financing_support.dta", ///
    keepusing(raise1 raise2 raise3 ///
              complete1 complete2 complete3 ///
              cum1 cum2 cum3 ///
              undisclosed1 undisclosed2 undisclosed3 ///
              duration_days observed next_event next_days ///
              next_amount next_n) ///
    assert(match) nogen

* 필요한 변수가 들어왔는지 확인
describe raise1 raise2 raise3 cum1 cum2 cum3

* 1. Cumulative next-round probability at fixed horizons, robust LPM.
* 4. ln(1 + cumulative USD), retaining no-round zeros under cutoff assumption.
forvalues h=1/3 {
    assert missing(raise`h') if complete`h' == 0
    assert missing(cum`h') if undisclosed`h' == 1
    reghdfe raise`h' `X', absorb(Region2 Industry2 Foundingyear) vce(robust)
    post `P' ("probability_`h'y") (_b[VD]) (_se[VD]) (e(N))
    estimates save "`D'/probability_`h'y.ster", replace
    gen double ln_cum_usd`h' = ln(1 + cum`h')
    assert ln_cum_usd`h' == 0 if cum`h' == 0
    assert missing(ln_cum_usd`h') if missing(cum`h')
    reghdfe ln_cum_usd`h' `X', absorb(Region2 Industry2 Foundingyear) vce(robust)
    estimates store logcum`h'
    post `P' ("cumulative_log1p_USD_`h'y") (_b[VD]) (_se[VD]) (e(N))
    estimates save "`D'/cumulative_`h'y.ster", replace
}
esttab logcum1 logcum2 logcum3 using "`D'/Panel_C_log_cumulative.csv", ///
    replace b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    stats(N r2 r2_a) title("Cumulative Equity Raised: ln(1 + USD)")
	
* 1. Next-round hazard. Common three-year follow-up cap; retain censored firms.
gen double stop3 = mdy(12,31,VDyear+3)-mdy(12,31,VDyear)
gen double surv_days = min(duration_days,1095) if observed == 1
gen byte event3 = next_event == 1 & next_days <= stop3 if observed == 1
gen byte surv_event = next_event == 1 & next_days <= 1095 if observed == 1
stset surv_days if observed == 1, failure(surv_event==1) id(firm_id)
stcox `X' `FE', nohr vce(robust)
post `P' ("next_round_log_hazard") (_b[VD]) (_se[VD]) (e(N))
estimates save "`D'/next_round_cox.ster", replace
* 2. Timing: KM survival and restricted mean waiting time, including censoring.
* RMST has a common 1095-day restriction and is unadjusted/descriptive;
* Weibull AFT log-time coefficient is parametric.
sts list, by(VD) at(365 730 1095)
stci, by(VD) rmean
sts graph, by(VD) xtitle("Days since end of VD/reference year") ///
    ytitle("Probability of no subsequent equity round") ///
    title("Supporting financing environment: next equity round")
graph export "`D'/next_equity_survival.png", replace
streg `X' `FE', distribution(weibull) time vce(robust)
post `P' ("waiting_time_weibull_logtime") (_b[VD]) (_se[VD]) (e(N))
estimates save "`D'/waiting_time_aft.ster", replace
* 3. First next-round amount conditional on raising within 3 years.
* Complete 3-year cohorts only; unknown amounts and ambiguous tied rounds excluded.
gen double ln_next_amount = ln(next_amount) if next_amount > 0 & !missing(next_amount)
reghdfe ln_next_amount `X' if complete3==1 & event3==1 & next_n==1, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
post `P' ("conditional_next_round_logUSD") (_b[VD]) (_se[VD]) (e(N))
estimates save "`D'/conditional_next_amount.ster", replace
postclose `P'


*Table 8:cox proportional hazard
* 관측 종료연도 설정
scalar T7_endyear = 2026

* 기업별 1행인지 확인
isid firm_id

* 재실행 시 기존 생성 변수 정리
foreach v in any_exit stop_year duration {
    capture drop `v'
}

* 상태값 확인
assert inlist(status, "acquired", "merged", ///
    "public", "defunct", "private")

* 사건 발생 여부
gen byte any_exit = inlist(status, ///
    "acquired", "merged", "public", "defunct")

* 관측 종료연도
gen double stop_year = .

* Private: 설정한 관측 종료연도까지 관측
replace stop_year = scalar(T7_endyear) ///
    if status == "private"

* Exit: 사건연도와 관측 종료연도 중 이른 연도까지 관측
* 사건연도가 없는 exit 기업은 결측으로 유지
replace stop_year = min(status_year, scalar(T7_endyear)) ///
    if any_exit == 1 & !missing(status_year)

* VD/reference year부터 관측 종료까지의 기간
gen double duration = stop_year - VDyear

* 연도 자료로 양의 관측기간을 계산할 수 없는 경우 제외
replace duration = . if duration <= 0

* 점검
count if any_exit == 1 & missing(status_year)
count if !missing(stop_year, VDyear) & stop_year <= VDyear
summarize duration, detail

scalar T7_endyear = 2026

capture drop fail_ma
capture drop fail_ipo
capture drop fail_defunct

gen byte fail_ma = ma == 1 & status_year > VDyear & status_year <= scalar(T7_endyear) & !missing(status_year, VDyear)

gen byte fail_ipo = ipo == 1 & status_year > VDyear & status_year <= scalar(T7_endyear) & !missing(status_year, VDyear)

gen byte fail_defunct = defunct == 1 & status_year > VDyear & status_year <= scalar(T7_endyear) & !missing(status_year, VDyear)

* 6개 열의 분석표본 통일
* 날짜 없는 exit, 기준연도 이전/동년 exit, 통제변수 결측은 제외
gen byte table7_sample = ///
    !missing(duration, VD, priorpatentdummy_VD, latestage_VD, ///
             ln_MoneyRaised_VD, NumofFundingRounds_VD, ///
             Region2, Industry2, VDyear) ///
    & duration > 0

tab status table7_sample, missing

* Column (1): M&A — VD + Region/Industry/Year FE
stset duration if table7_sample == 1, ///
    failure(fail_ma == 1) id(firm_id)

stcox VD Region2 Industry2 Foundingyear, nohr ///
    cformat(%9.3f) pformat(%5.3f)


stcox VD priorpatentdummy_VD latestage_VD ln_MoneyRaised_VD NumofFundingRounds_VD Region2 Industry2 Foundingyear, nohr ///
    cformat(%9.3f) pformat(%5.3f)

* Column (3): IPO — VD + Region/Industry/Year FE
stset duration if table7_sample == 1, ///
    failure(fail_ipo == 1) id(firm_id)

stcox VD Region2 Industry2 Foundingyear, nohr ///
    cformat(%9.3f) pformat(%5.3f)



stcox VD priorpatentdummy_VD latestage_VD ln_MoneyRaised_VD NumofFundingRounds_VD Region2 Industry2 Foundingyear, nohr ///
    cformat(%9.3f) pformat(%5.3f)


* Column (5): Defunct — VD + Region/Industry/Year FE
stset duration if table7_sample == 1, ///
    failure(fail_defunct == 1) id(firm_id)

stcox VD Region2 Industry2 Foundingyear, nohr ///
    cformat(%9.3f) pformat(%5.3f)


stcox VD priorpatentdummy_VD latestage_VD ln_MoneyRaised_VD NumofFundingRounds_VD Region2 Industry2 Foundingyear, nohr ///
    cformat(%9.3f) pformat(%5.3f)



*****Table 7.v2

* M&A
stset duration if table7_sample == 1, ///
    failure(fail_ma == 1) id(firm_id)

* 통제모형으로 분석표본 확정
stcox VD priorpatentdummy_VD latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear, nohr

capture drop ma_sample
gen byte ma_sample = e(sample)

* VD별 사건 수와 비율
tab VD fail_ma if ma_sample, row

* 전체 관측기간 / M&A까지 걸린 기간
tabstat duration if ma_sample, ///
    by(VD) statistics(n mean p50)

tabstat duration if ma_sample & fail_ma == 1, ///
    by(VD) statistics(n mean p50)

stsum if ma_sample, by(VD)

stcox VD if ma_sample, nohr

stcox VD i.Region2 i.Industry2 i.Foundingyear ///
    if ma_sample, nohr

stcox VD priorpatentdummy_VD latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear ///
    if ma_sample, nohr

*ipo
* 현재 통제모형의 실제 분석표본 고정
capture drop ipo_sample
gen byte ipo_sample = e(sample)

tab VD fail_ipo if ipo_sample, row

* 2. VD별 관측기간 및 IPO까지 걸린 기간
tabstat duration if ipo_sample, by(VD) statistics(n mean p50)
tabstat duration if ipo_sample & fail_ipo == 1, ///
    by(VD) statistics(n mean p50)

* 사건 수 / 총 관측시간
stsum if ipo_sample, by(VD)

stcox VD if ipo_sample, nohr

stcox VD i.Region2 i.Industry2 i.Foundingyear ///
    if ipo_sample, nohr

stcox VD priorpatentdummy_VD latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear ///
    if ipo_sample, nohr

* Defunct

stset duration if table7_sample == 1, ///
    failure(fail_defunct == 1) id(firm_id)

* 통제모형으로 분석표본 확정
stcox VD priorpatentdummy_VD latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear, nohr

capture drop defunct_sample
gen byte defunct_sample = e(sample)

* VD별 사건 수와 비율
tab VD fail_defunct if defunct_sample, row

tabstat duration if defunct_sample, ///
    by(VD) statistics(n mean p50)

tabstat duration if defunct_sample & fail_defunct == 1, ///
    by(VD) statistics(n mean p50)

stsum if defunct_sample, by(VD)

stcox VD if defunct_sample, nohr

stcox VD i.Region2 i.Industry2 i.Foundingyear ///
    if defunct_sample, nohr

stcox VD priorpatentdummy_VD latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear ///
    if defunct_sample, nohr
	
* Employee: original 611-firm specification (Word Table A4).
* Legacy employee observation date is unverified: lastdeal2vd1 is a sample
* selection variable, not a verified employee measurement year.
* Keep original earlystage (NOT latestage_VD) for historical replication.
* Existing data already contain these variables; no use/merge is necessary.
regress emp2025_2 VD i.lastdeal2vd1 ///
    if private==1 & inrange(lastdeal2vd1,1,3), vce(robust)
estimates store Employee_1

regress emp2025_2 VD patentdummybyfiling earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.lastdeal2vd1 i.Founding_Year ib4.Region2 ib3.Industry2 ///
    if private==1 & inrange(lastdeal2vd1,1,3), vce(robust)
estimates store Employee_2

regress emp2025_2 i.VD##ib0.patentdummybyfiling earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.lastdeal2vd1 i.Founding_Year ib4.Region2 ib3.Industry2 ///
    if private==1 & inrange(lastdeal2vd1,1,3), vce(robust)
estimates store Employee_3

regress emp2025_2 patentdummybyfiling i.VD##ib0.earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.lastdeal2vd1 i.Founding_Year ib4.Region2 ib3.Industry2 ///
    if private==1 & inrange(lastdeal2vd1,1,3), vce(robust)
estimates store Employee_4

regress emp2025_2 i.VD##ib0.patentdummybyfiling i.VD##ib0.earlystage ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.lastdeal2vd1 i.Founding_Year ib4.Region2 ib3.Industry2 ///
    if private==1 & inrange(lastdeal2vd1,1,3), vce(robust)
estimates store Employee_5

esttab Employee_1 Employee_2 Employee_3 Employee_4 Employee_5, ///
    b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) stats(N r2) ///
    title("Employees: original sample and specifications")


* Annual revenue regressions: these are NOT the Word A5/A6 descriptive tables.
* Retain missing revenue as missing; do not replace unavailable values by zero.
capture drop ln_revenue_t1 ln_revenue_t2 ln_revenue_t3
gen double ln_revenue_t1 = ln(1 + revenue_t1)
gen double ln_revenue_t2 = ln(1 + revenue_t2)
gen double ln_revenue_t3 = ln(1 + revenue_t3)
reghdfe ln_revenue_t1 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store Revenue_1

reghdfe ln_revenue_t2 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store Revenue_2

reghdfe ln_revenue_t3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store Revenue_3

esttab Revenue_1 Revenue_2 Revenue_3, ///
    b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) stats(N r2) ///
    title("Annual post-VD revenue: t+1, t+2, t+3")


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
***Other innovation measures
tatstast nocite_win3 breakthrough_win3 claims_win3 gunning_fog_win3 ari_win3 oldpat_win3 newcpc_win3 cite_breadth_win3 selfcite_win3, ///
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

*7-1
fracreg logit nocite_win3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear, vce(robust)
fracreg logit nocite_win3 i.VD##i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear, vce(robust)
fracreg logit nocite_win3 i.priorpatentdummy_VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear, vce(robust)
fracreg logit nocite_win3 i.VD##i.priorpatentdummy_VD  i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear, vce(robust)


*7-2
reghdfe breakthrough_win3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
reghdfe breakthrough_win3  i.VD##i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
reghdfe breakthrough_win3  i.priorpatentdummy_VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
reghdfe breakthrough_win3  i.VD##i.priorpatentdummy_VD ///
    i.VD##i.latestage_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)

*7-3
reghdfe ln_claims_win3 VD i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
reghdfe ln_claims_win3 i.VD##i.priorpatentdummy_VD i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
reghdfe ln_claims_win3 i.priorpatentdummy_VD i.VD##i.latestage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
reghdfe ln_claims_win3 i.VD##i.priorpatentdummy_VD ///
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


