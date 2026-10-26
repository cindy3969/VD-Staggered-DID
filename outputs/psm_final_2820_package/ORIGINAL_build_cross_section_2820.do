encode Revenue_Range, gen(Revenue_Range_)
drop Revenue_Range
rename Revenue_Range_ Revenue_Range
rename var117 emp2023

encode Region2, gen(Region2_)
drop Region2
rename Region2_ Region2

encode OperatingStatus, gen(OperatingStatus_)
drop OperatingStatus
rename OperatingStatus_ OperatingStatus

gen ln_MoneyRaised_VD = log(MoneyRaised_VD+1)
gen ln_fwd_rate_win3 = log(fwd_rate_win3+1)
gen ln_fwd_rate_win3 = log(fwd_rate_win3+1)
gen ln_fwd_rate_win3 = log(fwd_rate_win3+1)
gen ln_fwd_rate_win3 = log(fwd_rate_win3+1)
drop ln_fwd_rate_win3

gen ln_fwd_rate_win3 = log(fwd_rate_win3+1)
gen ln_fwd_rate_win3 = log(fwd_rate_win3+1)
gen ln_fwd_rate_win3 = log(fwd_rate_win3+1)
gen ln_fwd_rate_win3 = log(fwd_rate_win3+1)
gen ln_fwd_rate_win3 = log(fwd_rate_win3+1)


reg ln_fwd_rate_win3 VD patentdummybyfiling SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, replace dec(3) excel pvalue pdec(3)
reg ln_fwd_rate_win3 i.VD##i.patentdummybyfiling SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, append dec(3) excel pvalue pdec(3)
reg ln_fwd_rate_win3 patentdummybyfiling i.VD##i.SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, append dec(3) excel pvalue pdec(3)
reg ln_fwd_rate_win3 i.VD##i.patentdummybyfiling i.VD##i.SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, append dec(3) excel pvalue pdec(3)

reg ln_fwd_rate_win3 VD patentdummybyfiling SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, replace dec(3) excel pvalue pdec(3)
reg ln_fwd_rate_win3 i.VD##i.patentdummybyfiling SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, append dec(3) excel pvalue pdec(3)
reg ln_fwd_rate_win3 patentdummybyfiling i.VD##i.SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, append dec(3) excel pvalue pdec(3)
reg ln_fwd_rate_win3 i.VD##i.patentdummybyfiling i.VD##i.SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, append dec(3) excel pvalue pdec(3)

reg ln_fwd_rate_win3 VD patentdummybyfiling SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, replace dec(3) excel
reg ln_fwd_rate_win3 i.VD##i.patentdummybyfiling SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, append dec(3) excel
reg ln_fwd_rate_win3 patentdummybyfiling i.VD##i.SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, append dec(3) excel
reg ln_fwd_rate_win3 i.VD##i.patentdummybyfiling i.VD##i.SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, append dec(3) excel

reg ln_fwd_norm_cohort_win3 VD techcapa earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, replace dec(3) excel
reg ln_fwd_norm_cohort_win3 i.VD##i.techcapa earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, append dec(3) excel
reg ln_fwd_norm_cohort_win3 techcapa i.VD##i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, append dec(3) excel
reg ln_fwd_norm_cohort_win3 i.VD##i.techcapa i.VD##i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, append dec(3) excel


reg ln_fwd_rate_win3 VD patentdummybyfiling SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, replace dec(3) excel
reg ln_fwd_rate_win3 i.VD##i.patentdummybyfiling SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, append dec(3) excel
reg ln_fwd_rate_win3 patentdummybyfiling i.VD##i.SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, append dec(3) excel
reg ln_fwd_rate_win3 i.VD##i.patentdummybyfiling i.VD##i.SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2
outreg2 using results.xls, append dec(3) excel

gen ln_timetonextequity = log(timetonextequity+1)
gen timetonextequity_year = timetonextequity/365
gen ln_moneyraised_win3 = log(moneyraised_win3+1)
gen ln_moneyraised_win3 = log(moneyraised_win3+1)
gen ln_moneyraised_win3 = log(moneyraised_win3+1)
gen ln_moneyraised_win3 = log(moneyraised_win3+1)
gen ln_moneyraised_win3 = log(moneyraised_win3+1)

logit scaleupdummy VD patentdummybyfiling SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year i.Industry2 i.Region2, cluster(firm_id)

reg ln_timetonextequity VD ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib4.Region2 ib3.Industry2
outreg2 using results.xls, replace dec(3) pvalue excel
reg timetonextequity_year VD ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib4.Region2 ib3.Industry2
outreg2 using results.xls, append dec(3) pvalue excel

reg ln_moneyraised_y2 VD techcapa earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib4.Region2 ib3.Industry2 
outreg2 using results.xls, replace dec(3) pvalue excel
reg ln_moneyraised_y2 i.VD##ib0.techcapa earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib4.Region2 ib3.Industry2
outreg2 using results.xls, append dec(3) pvalue excel
reg ln_moneyraised_y2 i.VD##ib0.earlystage techcapa ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib4.Region2 ib3.Industry2
outreg2 using results.xls, append dec(3) pvalue excel
reg ln_moneyraised_y2 i.VD##ib0.techcapa i.VD##ib0.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib4.Region2 ib3.Industry2
outreg2 using results.xls, append dec(3) pvalue excel


reg ln_moneyraised_win1 i.VD##ib0.techcapa i.VD##ib0.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib3.Industry2 ib4.Region2
reg ln_moneyraised_win2 i.VD##ib0.nopatentdummy earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib3.Industry2 ib4.Region2
reg ln_moneyraised_win3 i.VD##ib0.nopatentdummy earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib3.Industry2 ib4.Region2
reg ln_moneyraised_win4 i.VD##ib0.nopatentdummy earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib3.Industry2 ib4.Region2
reg ln_moneyraised_win5 i.VD##ib0.nopatentdummy earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib3.Industry2 ib4.Region2

reg ln_moneyraised_win3 VD ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib3.Industry2 ib4.Region2 if patentbyfiling_win3
outreg2 using results.xls, replace dec(3) pvalue excel
reg ln_moneyraised_win3 VD ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib3.Industry2 ib4.Region2
outreg2 using results.xls, append dec(3) pvalue excel
reg ln_moneyraised_win3 VD ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib3.Industry2 ib4.Region2
outreg2 using results.xls, append dec(3) pvalue excel
reg ln_moneyraised_win3 VD ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib3.Industry2 ib4.Region2
outreg2 using results.xls, append dec(3) pvalue excel
reg ln_moneyraised_win3 VD ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib3.Industry2 ib4.Region2
outreg2 using results.xls, append dec(3) pvalue excel

gen nopatentdummy = 1 - patentdummy
gen earlystage = 1 - SeriesB

gen techcapa = 1 - nopatentdummy
reg ln_patentbyfiling_win2 VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2 
outreg2 using results.xls, replace dec(3) pvalue excel
reg ln_patentbyfiling_win2 i.VD##ib0.patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2 
outreg2 using results.xls, append dec(3) pvalue excel
reg ln_patentbyfiling_win2 patentdummybyfiling i.VD##ib0.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2 
outreg2 using results.xls, append dec(3) pvalue excel
reg ln_patentbyfiling_win2 i.VD##ib0.patentdummybyfiling i.VD##ib0.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2 
outreg2 using results.xls, append dec(3) pvalue excel

reg ln_patentbyfiling_win3 VD patentdummybyfiling SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2 if ln_patentbyfiling_win3 > 0
reg ln_patentbyfiling_win3 i.VD##ib0.patentdummybyfiling SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2 if ln_patentbyfiling_win3 > 0
reg ln_patentbyfiling_win3 VD patentdummybyfiling i.VD##ib0.SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2 if ln_patentbyfiling_win3 > 0
reg ln_patentbyfiling_win3 i.VD##ib0.patentdummybyfiling i.VD##ib0.SeriesB ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2 if ln_patentbyfiling_win3 > 0

gen timetoexit = exityear - VDyear 
gen timetoexit2 = exityear - Foundingyear

stcox VD 

probit badexit VD 
probit goodexit VD 
probit VD TimetoFirstVC

gen VDage = VDyear - Founding_Year


stset badexit2
stcox VD firmage 

stset firmage2, failure(goodexit2)
stcox VD 

stset firmage3, failure(goodexit3)
stcox VD 
* Cox PH model with VD only – coefficients (log-hazard)
stcox VD, nohr cformat(%9.3f) pformat(%5.3f) sformat(%8.3f)
stcox VD, cformat(%9.3f) pformat(%5.3f) sformat(%8.3f)


stset firmage2, failure(badexit2)
stcox VD
stset firmage3, failure(badexit3)
sts graph, by(VD) risktable ylabel(, format(%9.1f))
stcurve, survival at(VD = (0 1)) ylabel(, format(%9.1f))
stcurve, hazard



stset VDage3, failure(badexit3 == 1)
stsum
tab badexit3
summ VDage3 if badexit3 == 1
* bad exit 개수만 확인
tab badexit3

* VD별 bad exit rate
tab VD public3, row

* (4) VD=0 vs VD=1 그룹별 생존함수
stcurve, failure ///
    at1(VD = 0) at2(VD = 1) ///
    legend(order(1 "VC-only (VD=0)" 2 "VD-backed (VD=1)")) ///
    ylabel(, format(%9.1f)) ///
    title("Cox survival by VD status: Bad exit")
* (5) hazard 함수
stcurve, hazard ///
    title("Cox hazard: Bad exit")

* (6) 누적 hazard
stcurve, cumhaz ylabel(, format(%9.1f)) ///
    title("Cumulative hazard: Bad exit")

* (7) failure 함수 (1 - survival)
stcurve, failure ylabel(, format(%9.1f)) ///
    title("Failure (1-Survival): Bad exit")
stset VDage3, failure(badexit3 == 1)
stset VDage3, failure(acq3 == 1)
stset VDage3, failure(public3 == 1)
stcox VD, nohr cformat(%9.3f) pformat(%5.3f) sformat(%8.3f) //1
outreg2 using results1.xls, replace dec(3) excel pvalue pdec(3)

stcox VD patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2, nohr cformat(%9.3f) pformat(%5.3f) sformat(%8.3f) //2
outreg2 using results1.xls, append dec(3) excel pvalue pdec(3)

stcox i.VD##ib0.patentdummybyfiling earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2, nohr cformat(%9.3f) pformat(%5.3f) sformat(%8.3f) //3
outreg2 using results1.xls, append dec(3) excel pvalue pdec(3)

stcox patentdummybyfiling i.VD##ib0.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2, nohr cformat(%9.3f) pformat(%5.3f) sformat(%8.3f) //4
outreg2 using results1.xls, append dec(3) excel pvalue pdec(3)

stcox i.VD##ib0.patentdummybyfiling i.VD##ib0.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2, nohr cformat(%9.3f) pformat(%5.3f) sformat(%8.3f) //5
outreg2 using results1.xls, append dec(3) excel pvalue pdec(3)

capture erase "results.xls"

stset VDage4, failure(goodexit3 == 1)
stcox VD 

reg ln_patentbyfiling_win3 i.VD##ib0.nopatentdummy earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Foundingyear ib4.Region2 ib3.Industry2

gen ln_employees = log(employees+1)
reg ln_employees VD, vce(robust)
gen obsyear = exityear - Founding_Year

reg ln_employees VD techcapa earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib4.Region2 ib3.Industry2
reg ln_moneyraised_win2 i.VD##ib0.nopatentdummy earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib3.Industry2 ib4.Region2
reg ln_moneyraised_win3 i.VD##ib0.nopatentdummy earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib3.Industry2 ib4.Region2
reg ln_moneyraised_win4 i.VD##ib0.nopatentdummy earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib3.Industry2 ib4.Region2
reg ln_moneyraised_win5 i.VD##ib0.nopatentdummy earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib3.Industry2 ib4.Region2

* 1) employees가 관측된 기준연도 만들기
gen emp_asof_year = cond(alive==1, 2025, exityear)   // exit_year 변수명에 맞춰 수정
gen emp_age = emp_asof_year - Founding_Year
replace emp_age = . if emp_age<0

* 2) 연령/기준연도(및 산업/지역)로 employees를 설명하고 잔차만 뽑기
reg ln_employees c.emp_age i.emp_asof_year ib4.Region2 ib3.Industry2, vce(robust)
predict ln_emp_adj, resid

* 3) 본 회귀에는 조정된 size(잔차) 사용
reg ln_employees VD techcapa earlystage ln_MoneyRaised_VD NumofFundingRounds_VD ///
    Founding_Year ln_emp_adj ib4.Region2 ib3.Industry2, vce(robust)

reg ln_employees VD techcapa earlystage ln_MoneyRaised_VD NumofFundingRounds_VD ///
    Founding_Year ib4.Region2 ib3.Industry2 if alive==1, vce(robust)
reg ln_employees i.VD##ib0.techcapa earlystage ln_MoneyRaised_VD NumofFundingRounds_VD ///
    c.emp_age i.emp_asof_year ib4.Region2 ib3.Industry2 if alive==1, vce(robust)
reg ln_employees i.VD##ib0.earlystage techcapa ln_MoneyRaised_VD NumofFundingRounds_VD ///
    c.emp_age i.emp_asof_year ib4.Region2 ib3.Industry2 if alive==1, vce(robust)
reg ln_employees i.VD##ib0.techcapa i.VD##ib0.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD ///
    c.emp_age i.emp_asof_year ib4.Region2 ib3.Industry2 if alive==1, vce(robust)

reg ln_employees VD techcapa earlystage ln_MoneyRaised_VD NumofFundingRounds_VD ///
    emp_age emp_asof_year ib4.Region2 ib3.Industry2, vce(robust)
outreg2 using results2.xls, replace dec(3) pvalue excel
reg ln_employees i.VD##ib0.techcapa earlystage ln_MoneyRaised_VD NumofFundingRounds_VD ///
    emp_age emp_asof_year ib4.Region2 ib3.Industry2, vce(robust)
outreg2 using results2.xls, append dec(3) pvalue excel
reg ln_employees i.VD##ib0.earlystage techcapa ln_MoneyRaised_VD NumofFundingRounds_VD ///
    emp_age emp_asof_year ib4.Region2 ib3.Industry2, vce(robust)
outreg2 using results2.xls, append dec(3) pvalue excel
reg ln_employees i.VD##ib0.techcapa i.VD##ib0.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD ///
    emp_age emp_asof_year ib4.Region2 ib3.Industry2, vce(robust)
outreg2 using results2.xls, append dec(3) pvalue excel



tabstat VD ln_patentbyfiling_win3 ln_fwd_norm_cohort_win3 ln_moneyraised_y2 acq3 public3 badexit3 techcapa earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year California Massachusetts NewYork BioHealthcare Hardware Software, statistics(mean sd) 

ologit emp2023 i.VD##ib0.patentdummybyfiling i.VD##ib0.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD Founding_Year ib4.Region2 ib3.Industry2, vce(robust)

tabstat emp2023, by(VD) stat(n mean) columns(statistics)

tabstat emp2023_ord if VDyear==2018 & private==1, by(VD) stat(n mean) columns(statistics)

tab emp2023 VD if VDyear==2020 & private==1, col nofreq


tab Revenue_Range, missing
describe Revenue_Range_ord
codebook Revenue_Range_ord
tab Revenue_Range_ord, nolabel


codebook Revenue_Range
tab Revenue_Range, nolabel
label list 
* emp2023이 value label 달린 숫자변수라는 전제 (지금 화면처럼)

gen Revenue_Range_ord = .
replace Revenue_Range_ord = 1 if Revenue_Range==8              // 1-10
replace Revenue_Range_ord = 2 if Revenue_Range==5              // 11-50
replace Revenue_Range_ord = 3 if Revenue_Range==3              // 51-100
replace Revenue_Range_ord = 4 if Revenue_Range==7              // 101-250
replace Revenue_Range_ord = 5 if Revenue_Range==6              // 251-500
replace Revenue_Range_ord = 6 if Revenue_Range==1              // 501-1000
replace Revenue_Range_ord = 7 if Revenue_Range==6              // 1001-5000
replace Revenue_Range_ord = 8 if Revenue_Range==4              // 5001-10000
replace Revenue_Range_ord = 9 if Revenue_Range==2              // 10001+

label define Revenue_Range 1 "Less than $1M" 2 "$1M to $10M" 3 "$10M to $50M" 4 "$50M to $100M" 5 "$100M to $500M" 6 "$500M to $1B" 7 "$1B to $10B" 8 "$10B+" 9 "10001", replace
label values Revenue_Range 

* 확인: 오름차순으로 제대로 됐는지
tab emp2023_ord, missing
asdoc tab emp2023_ord, nolabel
2023
tabstat Revenue_Range_ord if VDyear==2022, by(VD) stat(n mean)
tabstat Revenue_Range_ord if VDyear2==2022 & private==1, by(VD) stat(n mean)

tabstat emp2025 if VDyear2==2024, by(VD) stat(n mean)

sort firm_id

gen ln_MoneyRaised_VD2 = log(MoneyRaised_VD2+1)
gen ln_emp2025 = log(emp2025+1)

reg emp2025 VD if VDyear2==2022 & private==1, vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel
reg emp2025 VD patentdummybyfiling earlystage ln_MoneyRaised_VD2 NumofFundingRounds_VD2  Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2022 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel
reg emp2025 i.VD##ib0.patentdummybyfiling earlystage ln_MoneyRaised_VD2 NumofFundingRounds_VD2     Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2022 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel
reg emp2025 i.VD##ib0.earlystage patentdummybyfiling ln_MoneyRaised_VD2 NumofFundingRounds_VD2     Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2022 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel
reg emp2025 i.VD##ib0.patentdummybyfiling i.VD##ib0.earlystage ln_MoneyRaised_VD2 NumofFundingRounds_VD2 Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2022 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel

reg emp2025 VD if VDyear2==2023 & private==1, vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel
reg emp2025 VD patentdummybyfiling earlystage ln_MoneyRaised_VD2 NumofFundingRounds_VD2  Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2023 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel
reg emp2025 i.VD##ib0.patentdummybyfiling earlystage ln_MoneyRaised_VD2 NumofFundingRounds_VD2     Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2023 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel
reg emp2025 i.VD##ib0.earlystage patentdummybyfiling ln_MoneyRaised_VD2 NumofFundingRounds_VD2     Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2023 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel
reg emp2025 i.VD##ib0.patentdummybyfiling i.VD##ib0.earlystage ln_MoneyRaised_VD2 NumofFundingRounds_VD2 Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2023 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel



tabstat emp2025 if VDyear2==2022 & private==1, by(VD) stat(n mean p50 p75 p90 p95 p99 max)

sum emp2025 if VDyear2==2022 & private==1, detail
tabstat emp2025 if VDyear2==2022 & private==1, stat(n mean p50 p90 p95 p99 max)

quietly summarize emp2025 if VDyear2==2022 & private==1, detail
scalar p2  = r(p2)
scalar p80 = r(p80)

*4year
reg emp2025 VD if VDyear2==2023 & private==1, vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel
reg emp2025 VD patentdummybyfiling earlystage ln_MoneyRaised_VD2 NumofFundingRounds_VD2  i.Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2023 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel
reg emp2025 i.VD##ib0.patentdummybyfiling earlystage ln_MoneyRaised_VD2 NumofFundingRounds_VD2  i.Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2023 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel
reg emp2025 i.VD##ib0.earlystage patentdummybyfiling ln_MoneyRaised_VD2 NumofFundingRounds_VD2  i.Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2023 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel
reg emp2025 i.VD##ib0.patentdummybyfiling i.VD##ib0.earlystage ln_MoneyRaised_VD2 NumofFundingRounds_VD2  i.Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2023 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel


reg emp2025 VD if VDyear2==2022 & private==1, vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel
reg emp2025 VD patentdummybyfiling earlystage ln_MoneyRaised_VD2 NumofFundingRounds_VD2  i.Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2022 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel
reg emp2025 i.VD##ib0.patentdummybyfiling earlystage ln_MoneyRaised_VD2 NumofFundingRounds_VD2  i.Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2022 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel
reg emp2025 i.VD##ib0.earlystage patentdummybyfiling ln_MoneyRaised_VD2 NumofFundingRounds_VD2  i.Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2022 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel
reg emp2025 i.VD##ib0.patentdummybyfiling i.VD##ib0.earlystage ln_MoneyRaised_VD2 NumofFundingRounds_VD2  i.Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2022 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel

reg emp2025 VD if VDyear2==2022 & inrange(emp2025, p2, p99), vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel
reg emp2025 VD patentdummybyfiling earlystage ln_MoneyRaised_VD2 NumofFundingRounds_VD2  i.Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2022 & inrange(emp2025, p2, p99), vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel
reg emp2025 i.VD##ib0.patentdummybyfiling earlystage ln_MoneyRaised_VD2 NumofFundingRounds_VD2  i.Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2022 & inrange(emp2025, p2, p99), vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel
reg emp2025 i.VD##ib0.earlystage patentdummybyfiling ln_MoneyRaised_VD2 NumofFundingRounds_VD2  i.Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2022 & inrange(emp2025, p2, p99), vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel
reg emp2025 i.VD##ib0.patentdummybyfiling i.VD##ib0.earlystage ln_MoneyRaised_VD2 NumofFundingRounds_VD2 i.Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2022 & inrange(emp2025, p2, p99), vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel

reg emp2025 VD if VDyear2==2021 & private==1, vce(robust)
outreg2 using results.xls, replace dec(3) pvalue excel
reg emp2025 VD patentdummybyfiling earlystage ln_MoneyRaised_VD2 NumofFundingRounds_VD2  i.Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2021 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel
reg emp2025 i.VD##ib0.patentdummybyfiling earlystage ln_MoneyRaised_VD2 NumofFundingRounds_VD2  i.Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2021 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel
reg emp2025 i.VD##ib0.earlystage patentdummybyfiling ln_MoneyRaised_VD2 NumofFundingRounds_VD2  i.Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2021 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel
reg emp2025 i.VD##ib0.patentdummybyfiling i.VD##ib0.earlystage ln_MoneyRaised_VD2 NumofFundingRounds_VD2 i.Founding_Year ib4.Region2 ib3.Industry2 if VDyear2==2021 & private==1, vce(robust)
outreg2 using results.xls, append dec(3) pvalue excel




reg emp2025 VD if VDyear2==2022 & inrange(emp2025, p2, p99), vce(robust)

reg emp2025 VD if VDyear2==2022 & inrange(emp2025, p2, p99), vce(robust)

ssc install winsor2
keep if VDyear2==2022 & private==1

*VD=1/0 cutoff 5%,95%
bysort VD: egen p5  = pctile(emp2025), p(5)
bysort VD: egen p95 = pctile(emp2025), p(95)

*one-sided 5% list
* VD=1 하위 5%
list firm_id VD emp2025 p5 p95 if VD==1 & emp2025<=p5, clean noobs
list firm_id VD emp2025 p5 p95 if VD==0 & emp2025<=p5, clean noobs
list firm_id VD emp2025 p5 p95 if emp2025<=p5, clean noobs

* VD=0 상위 5%
list firm_id VD emp2025 p5 p95 if emp2025>=p95, clean noobs

list firm_id VD emp2025 p5 p95 if emp2025>=p95, clean noobs

restore




