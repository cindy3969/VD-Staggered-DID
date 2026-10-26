**install
*capture which reghdfe
*if _rc ssc install reghdfe, replace
*capture which esttab
*if _rc ssc install estout, replace
***

version 19
clear all
set more off

global ROOT "C:/Users/user/Documents/VD/outputs/psm_final_2820_package"
capture mkdir "$ROOT/table3_application_results"
global OUT "$ROOT/table3_application_results"

capture log close
log using "$OUT/Table3_patent_application_win3.log", text replace
use "$ROOT/table3_current_2820_cross_section_v2.dta", clear

* DV = ln(1 + number of patent applications filed in VD+1 through VD+3).
rename patentdummybyfiling Priorpatent_VD
rename earlystage Earlystage_VD
gen ln_patentbyfiling_win3_2 = log(patentbyfiling_win3_2+1)
gen ln_priorpatent_VD_2 = log(priorpatent_VD_2+1)

gen nopriorpatentdummy_VD = 1 - priorpatentdummy_VD
gen ln_grantedbyfiling_win3 = log(grantedpatentbyfiling_win3+1)
gen ln_grantedbyfiling_norm_win3 = log(grantedpatentbyfiling_norm_win3+1)

gen ln_norm_cite_perpat_win3_v1 = log(norm_cite_perpat_win3_v1+1)
gen ln_norm_cite_perpat_win3_v2 = log(norm_cite_perpat_win3_v2+1)
gen ln_norm_cite_perpat_win3_v3 = log(norm_cite_perpat_win3_v3+1)
gen ln_norm_cite_perpat_win3_v4 = log(norm_cite_perpat_win3_v4+1)
gen ln_norm_cite_perpat_win3_vv1 = log(norm_cite_perpat_win3_vv1+1)
gen ln_norm_cite_perpat_win3_vv2 = log(norm_cite_perpat_win3_vv2+1)
gen ln_norm_cite_perpat_win3_vv3 = log(norm_cite_perpat_win3_vv3+1)
gen ln_norm_cite_perpat_win3_vv4 = log(norm_cite_perpat_win3_vv4+1)

gen ln_moneyraised_win3 = log(moneyraised_win3+1)
gen ln_moneyraised_t1 = log(moneyraised_t1+1)
gen ln_moneyraised_t2 = log(moneyraised_t2+1)
gen ln_moneyraised_t3 = log(moneyraised_t3+1)

tab Industry2, gen(ind_)
tab Region2,   gen(reg_)

rename Follow_on_Equity_Raised_win3 equityraised_win3
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
    gen ln_equityraised_t`t' = ln(1 + equityraised_t`t')
}

rename m_a ma

gen ln_revenue_t1 = log(revenue_t1+1)
gen ln_revenue_t2 = log(revenue_t2+1)
gen ln_revenue_t3 = log(revenue_t3+1)

rename grantedpatentbyfiling_norm_win3  grantedbyfiling_norm_win3 

gen double ln_vdsupply = ln(1 + vdsupply)
gen double ln_numberofvddeals = ln(1 + numberofvddeals)

******************************ANALYSES*****************************
* Table1: Summary statistics
tabstat patent_application_win3 VD nopriorpatentdummy_VD Earlystage_VD MoneyRaised_VD NumofFundingRounds_VD ind_1 ind_2 ind_4 reg_1 reg_2 reg_3, ///
 statistics(N mean sd min max) columns(statistics)
 
tabstat norm_cite_perpat_win3_v1 norm_cite_perpat_win3_v2 norm_cite_perpat_win3_v3, ///
 statistics(N mean sd min max) columns(statistics)
 

* Table 3: Patent quantity
reghdfe ln_grantedbyfiling_norm_win3 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel

reghdfe ln_grantedbyfiling_norm_win3 i.VD##i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel

reghdfe ln_grantedbyfiling_norm_win3 nopriorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel

reghdfe ln_grantedbyfiling_norm_win3 i.VD##i.nopriorpatentdummy_VD ///
    i.VD##i.Earlystage_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel


* Table 4: Patent quality
reghdfe ln_norm_cite_perpat_win3_v4 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel

reghdfe ln_norm_cite_perpat_win3_v4 i.VD##i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel

reghdfe ln_norm_cite_perpat_win3_v4 i.nopriorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel

reghdfe ln_norm_cite_perpat_win3_v4 i.VD##i.nopriorpatentdummy_VD ///
    i.VD##i.Earlystage_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel

* Table 5: follow on equity raised 
reghdfe ln_moneyraised_win3 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel

reghdfe ln_moneyraised_win3 i.VD##i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel

reghdfe ln_moneyraised_win3 i.nopriorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel

reghdfe ln_moneyraised_win3 i.VD##i.nopriorpatentdummy_VD ///
    i.VD##i.Earlystage_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel


* Table 6: annual follow on equity raised 
reghdfe ln_moneyraised_t1 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel

reghdfe ln_moneyraised_t2 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel

reghdfe ln_equityraised_t3 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel


*Table 7:cox proportional hazard
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
    !missing(duration, VD, nopriorpatentdummy_VD, Earlystage, ///
             ln_MoneyRaised_VD, NumofFundingRounds_VD, ///
             Region2, Industry2, VDyear) ///
    & duration > 0

tab status table7_sample, missing

* Column (1): M&A — VD + Region/Industry/Year FE
stset duration if table7_sample == 1, ///
    failure(fail_ma == 1) id(firm_id)

stcox VD Region2 Industry2 Foundingyear, nohr ///
    cformat(%9.3f) pformat(%5.3f)

estimates store T7_1

stcox VD nopriorpatentdummy_VD Earlystage_VD ln_MoneyRaised_VD NumofFundingRounds_VD Region2 Industry2 Foundingyear, nohr ///
    cformat(%9.3f) pformat(%5.3f)

estimates store T7_2
* Column (3): IPO — VD + Region/Industry/Year FE
stset duration if table7_sample == 1, ///
    failure(fail_ipo == 1) id(firm_id)

stcox VD Region2 Industry2 Foundingyear, nohr ///
    cformat(%9.3f) pformat(%5.3f)

estimates store T7_3


stcox VD nopriorpatentdummy_VD Earlystage_VD ln_MoneyRaised_VD NumofFundingRounds_VD Region2 Industry2 Foundingyear, nohr ///
    cformat(%9.3f) pformat(%5.3f)

estimates store T7_4

* Column (5): Defunct — VD + Region/Industry/Year FE
stset duration if table7_sample == 1, ///
    failure(fail_defunct == 1) id(firm_id)

stcox VD Region2 Industry2 Foundingyear, nohr ///
    cformat(%9.3f) pformat(%5.3f)

estimates store T7_5

stcox VD nopriorpatentdummy_VD Earlystage_VD ln_MoneyRaised_VD NumofFundingRounds_VD Region2 Industry2 Foundingyear, nohr ///
    cformat(%9.3f) pformat(%5.3f)

estimates store T7_6


*****Table 7.v2

* M&A
stset duration if table7_sample == 1, ///
    failure(fail_ma == 1) id(firm_id)

* 통제모형으로 분석표본 확정
stcox VD nopriorpatentdummy_VD Earlystage_VD ///
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

stcox VD nopriorpatentdummy_VD Earlystage_VD ///
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

stcox VD nopriorpatentdummy_VD Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear ///
    if ipo_sample, nohr

* Defunct

stset duration if table7_sample == 1, ///
    failure(fail_defunct == 1) id(firm_id)

* 통제모형으로 분석표본 확정
stcox VD nopriorpatentdummy_VD Earlystage_VD ///
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

stcox VD nopriorpatentdummy_VD Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear ///
    if defunct_sample, nohr
	
* Table 8: Employee
reghdfe ln_moneyraised_t1 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel

reghdfe ln_moneyraised_t2 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel

reghdfe ln_equityraised_t3 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel


* Table 10: Revenue
reghdfe ln_revenue_t1 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel

reghdfe ln_revenue_t2 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel

reghdfe ln_revenue_t2 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel


*******************APPENDIX********************
* Table A1: IV 2SLS
* (1) Second stage: 2SLS
ivreghdfe ln_grantedbyfiling_norm_win3 ///
    nopriorpatentdummy_VD Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    (VD = ln_vdsupply), ///
    absorb(Region2 Industry2 Foundingyear) robust first

estimates store IV_second
gen byte iv_sample = e(sample)

scalar CD_F = e(cdf)
scalar KP_F = e(widstat)

* (2) First stage: 동일한 추정 표본 사용
reghdfe VD ln_vdsupply ///
    nopriorpatentdummy_VD Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    if iv_sample == 1, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)

test ln_vdsupply
scalar excluded_IV_F = r(F)
estimates store IV_first


* Table A2: patenting firms only
reghdfe ln_grantedbyfiling_norm_win3 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    if grantedbyfiling_norm_win3 > 0 & !missing(grantedbyfiling_norm_win3), ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results_positive.xls, replace dec(3) pvalue excel

reghdfe ln_grantedbyfiling_norm_win3 i.VD##i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    if grantedbyfiling_norm_win3 > 0 & !missing(grantedbyfiling_norm_win3), ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results_positive.xls, append dec(3) pvalue excel

reghdfe ln_grantedbyfiling_norm_win3 nopriorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    if grantedbyfiling_norm_win3 > 0 & !missing(grantedbyfiling_norm_win3), ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results_positive.xls, append dec(3) pvalue excel

reghdfe ln_grantedbyfiling_norm_win3 i.VD##i.nopriorpatentdummy_VD ///
    i.VD##i.Earlystage_VD ln_MoneyRaised_VD NumofFundingRounds_VD ///
    if grantedbyfiling_norm_win3 > 0 & !missing(grantedbyfiling_norm_win3), ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results_positive.xls, append dec(3) pvalue excel

* Table A3: Table 7 M&A with moderating effect 
* 기존 생성 변수 정리
capture drop duration
capture drop exit_year
capture drop fail_ma
capture drop fail_ipo
capture drop fail_defunct
capture drop table7_sample

* 상태 더미 확인
assert inlist(ma, 0, 1)
assert inlist(ipo, 0, 1)
assert inlist(defunct, 0, 1)
assert ma + ipo + defunct <= 1

* 사건 기업은 사건 연도까지, 그 외 기업은 2026년까지 관측
gen double exit_year = 2026

replace exit_year = status_year ///
    if (ma == 1 | ipo == 1 | defunct == 1) ///
    & !missing(status_year) & status_year <= 2026

* 사건 연도를 모르는 exit 기업은 기간을 임의로 부여하지 않음
replace exit_year = . ///
    if (ma == 1 | ipo == 1 | defunct == 1) ///
    & missing(status_year)

* 분석 기간
gen double duration = exit_year - VDyear + 1 ///
    if !missing(exit_year, VDyear) ///
    & exit_year >= VDyear & VDyear <= 2026

* 사건 유형
gen byte fail_ma = ///
    ma == 1 & !missing(status_year) & status_year <= 2026

gen byte fail_ipo = ///
    ipo == 1 & !missing(status_year) & status_year <= 2026

gen byte fail_defunct = ///
    defunct == 1 & !missing(status_year) & status_year <= 2026

* 공통 분석표본
gen byte table7_sample = ///
    !missing(duration, firm_id, VD, ///
             nopriorpatentdummy_VD, Earlystage_VD, ///
             ln_MoneyRaised_VD, NumofFundingRounds_VD, ///
             Region2, Industry2, Foundingyear) ///
    & duration > 0


* M&A 사건 설정
stset duration if table7_sample == 1, ///
    failure(fail_ma == 1) id(firm_id)
	
* 두 조절효과를 포함한 모형으로 공통 분석표본 확정
stcox i.VD##i.nopriorpatentdummy_VD ///
    i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear, nohr

capture drop ma_sample
gen byte ma_sample = e(sample)


* (1) 기본모형
stcox i.VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear ///
    if ma_sample == 1, nohr

outreg2 using Table_A3.xls, replace excel dec(3) pvalue ///
    ctitle(Model 1) ///
    keep(1.VD 1.nopriorpatentdummy_VD 1.Earlystage_VD ///
         ln_MoneyRaised_VD NumofFundingRounds_VD) ///
    addtext(Region FE, Yes, Industry FE, Yes, Founding-year FE, Yes) ///
    addstat(Number of failures, e(N_fail))


* (2) VD × No Prior Patent
stcox i.VD##i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear ///
    if ma_sample == 1, nohr

outreg2 using Table_A3.xls, append excel dec(3) pvalue ///
    ctitle(Model 2) ///
    keep(1.VD 1.VD#1.nopriorpatentdummy_VD ///
         1.nopriorpatentdummy_VD 1.Earlystage_VD ///
         ln_MoneyRaised_VD NumofFundingRounds_VD) ///
    addtext(Region FE, Yes, Industry FE, Yes, Founding-year FE, Yes) ///
    addstat(Number of failures, e(N_fail))


* (3) VD × Early Stage
stcox i.nopriorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear ///
    if ma_sample == 1, nohr

outreg2 using Table_A3.xls, append excel dec(3) pvalue ///
    ctitle(Model 3) ///
    keep(1.VD 1.VD#1.Earlystage_VD ///
         1.nopriorpatentdummy_VD 1.Earlystage_VD ///
         ln_MoneyRaised_VD NumofFundingRounds_VD) ///
    addtext(Region FE, Yes, Industry FE, Yes, Founding-year FE, Yes) ///
    addstat(Number of failures, e(N_fail))


* (4) 두 조절효과 모두 포함
stcox i.VD##i.nopriorpatentdummy_VD ///
    i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear ///
    if ma_sample == 1, nohr

outreg2 using Table_A3.xls, append excel dec(3) pvalue ///
    ctitle(Model 4) ///
    keep(1.VD 1.VD#1.nopriorpatentdummy_VD ///
         1.VD#1.Earlystage_VD ///
         1.nopriorpatentdummy_VD 1.Earlystage_VD ///
         ln_MoneyRaised_VD NumofFundingRounds_VD) ///
    addtext(Region FE, Yes, Industry FE, Yes, Founding-year FE, Yes) ///
    addstat(Number of failures, e(N_fail))
	
* Table A4: Table 7 IPO with moderating effect 
* IPO 사건 설정
stset duration if table7_sample == 1, ///
    failure(fail_ipo == 1) id(firm_id)

* 두 조절효과를 포함한 모형으로 공통 분석표본 확정
stcox i.VD##i.nopriorpatentdummy_VD ///
    i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear, nohr

capture drop ipo_sample
gen byte ipo_sample = e(sample)


* (1) 기본모형
stcox i.VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear ///
    if ipo_sample == 1, nohr

outreg2 using Table_IPO.xls, replace excel dec(3) pvalue ///
    ctitle(Model 1) ///
    keep(1.VD 1.nopriorpatentdummy_VD 1.Earlystage_VD ///
         ln_MoneyRaised_VD NumofFundingRounds_VD) ///
    addtext(Region FE, Yes, Industry FE, Yes, Founding-year FE, Yes) ///
    addstat(Number of failures, e(N_fail))


* (2) VD × No Prior Patent
stcox i.VD##i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear ///
    if ipo_sample == 1, nohr

outreg2 using Table_IPO.xls, append excel dec(3) pvalue ///
    ctitle(Model 2) ///
    keep(1.VD 1.VD#1.nopriorpatentdummy_VD ///
         1.nopriorpatentdummy_VD 1.Earlystage_VD ///
         ln_MoneyRaised_VD NumofFundingRounds_VD) ///
    addtext(Region FE, Yes, Industry FE, Yes, Founding-year FE, Yes) ///
    addstat(Number of failures, e(N_fail))


* (3) VD × Early Stage
stcox i.nopriorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear ///
    if ipo_sample == 1, nohr

outreg2 using Table_IPO.xls, append excel dec(3) pvalue ///
    ctitle(Model 3) ///
    keep(1.VD 1.VD#1.Earlystage_VD ///
         1.nopriorpatentdummy_VD 1.Earlystage_VD ///
         ln_MoneyRaised_VD NumofFundingRounds_VD) ///
    addtext(Region FE, Yes, Industry FE, Yes, Founding-year FE, Yes) ///
    addstat(Number of failures, e(N_fail))


* (4) 두 조절효과 모두 포함
stcox i.VD##i.nopriorpatentdummy_VD ///
    i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear ///
    if ipo_sample == 1, nohr

outreg2 using Table_IPO.xls, append excel dec(3) pvalue ///
    ctitle(Model 4) ///
    keep(1.VD 1.VD#1.nopriorpatentdummy_VD ///
         1.VD#1.Earlystage_VD ///
         1.nopriorpatentdummy_VD 1.Earlystage_VD ///
         ln_MoneyRaised_VD NumofFundingRounds_VD) ///
    addtext(Region FE, Yes, Industry FE, Yes, Founding-year FE, Yes) ///
    addstat(Number of failures, e(N_fail))
* Table A5: Table 7 Defunct with moderating effect 

* Defunct 사건 설정
stset duration if table7_sample == 1, ///
    failure(fail_defunct == 1) id(firm_id)

* 두 조절효과를 포함한 모형으로 공통 분석표본 확정
stcox i.VD##i.nopriorpatentdummy_VD ///
    i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear, nohr

capture drop defunct_sample
gen byte defunct_sample = e(sample)


* (1) 기본모형
stcox i.VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear ///
    if defunct_sample == 1, nohr

outreg2 using Table_Defunct.xls, replace excel dec(3) pvalue ///
    ctitle(Model 1) ///
    keep(1.VD 1.nopriorpatentdummy_VD 1.Earlystage_VD ///
         ln_MoneyRaised_VD NumofFundingRounds_VD) ///
    addtext(Region FE, Yes, Industry FE, Yes, Founding-year FE, Yes) ///
    addstat(Number of failures, e(N_fail))


* (2) VD × No Prior Patent
stcox i.VD##i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear ///
    if defunct_sample == 1, nohr

outreg2 using Table_Defunct.xls, append excel dec(3) pvalue ///
    ctitle(Model 2) ///
    keep(1.VD 1.VD#1.nopriorpatentdummy_VD ///
         1.nopriorpatentdummy_VD 1.Earlystage_VD ///
         ln_MoneyRaised_VD NumofFundingRounds_VD) ///
    addtext(Region FE, Yes, Industry FE, Yes, Founding-year FE, Yes) ///
    addstat(Number of failures, e(N_fail))


* (3) VD × Early Stage
stcox i.nopriorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear ///
    if defunct_sample == 1, nohr

outreg2 using Table_Defunct.xls, append excel dec(3) pvalue ///
    ctitle(Model 3) ///
    keep(1.VD 1.VD#1.Earlystage_VD ///
         1.nopriorpatentdummy_VD 1.Earlystage_VD ///
         ln_MoneyRaised_VD NumofFundingRounds_VD) ///
    addtext(Region FE, Yes, Industry FE, Yes, Founding-year FE, Yes) ///
    addstat(Number of failures, e(N_fail))


* (4) 두 조절효과 모두 포함
stcox i.VD##i.nopriorpatentdummy_VD ///
    i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear ///
    if defunct_sample == 1, nohr

outreg2 using Table_Defunct.xls, append excel dec(3) pvalue ///
    ctitle(Model 4) ///
    keep(1.VD 1.VD#1.nopriorpatentdummy_VD ///
         1.VD#1.Earlystage_VD ///
         1.nopriorpatentdummy_VD 1.Earlystage_VD ///
         ln_MoneyRaised_VD NumofFundingRounds_VD) ///
    addtext(Region FE, Yes, Industry FE, Yes, Founding-year FE, Yes) ///
    addstat(Number of failures, e(N_fail))

***Other innovation measures
* Table A7: patent readability
*7-1
reghdfe gunning_fog_mean_win3 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel

*reghdfe gunning_fog_mean_win3 i.VD##i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
*reghdfe gunning_fog_mean_win3 i.nopriorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
*reghdfe gunning_fog_mean_win3 i.VD##i.nopriorpatentdummy_VD ///
    i.VD##i.Earlystage_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)

*7-2
reghdfe ari_mean_win3 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel
*7-3
reghdfe neg_flesch_mean_win3 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)

*8-1
gen ln_figures_win3 = log(figures_mean_win3+1)
reghdfe ln_figures_win3 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
*8-2
gen ln_sheets_win3 = log(sheets_mean_win3+1)
reghdfe ln_sheets_win3 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
*9-1
*reghdfe claims_mean_win3 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
*9-2
*reghdfe indep_claims_mean_win3 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
*9-3
*reghdfe dep_claims_mean_win3 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
*10
*reghdfe grant_rate_win3 VD i.nopriorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)




