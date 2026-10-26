use "20240117_2010 to 2015 firms.dta", clear
preserve

* controls construction
encode Region1, gen(Region1_)
drop Region1
rename Region1_ Region1

encode Region2, gen(Region2_)
drop Region2
rename Region2_ Region2

encode Revenue_Range, gen(Revenue_Range_)
drop Revenue_Range
rename Revenue_Range_ Revenue_Range

encode OperatingStatus, gen(OperatingStatus_)
drop OperatingStatus
rename OperatingStatus_ OperatingStatus

encode Industry1, gen(Industry1_)
drop Industry1
rename Industry1_ Industry1

encode Industry2, gen(Industry2_)
drop Industry2
rename Industry2_ Industry2

encode NumberOfEmployees_Range, gen(NumberOfEmployees_Range_)
drop NumberOfEmployees_Range
rename NumberOfEmployees_Range_ NumberOfEmployees_Range

encode Total_EquityFunding_Amount, gen(Total_EquityFunding_Amount_)
drop Total_EquityFunding_Amount
rename Total_EquityFunding_Amount_ Total_EquityFunding_Amount

encode IPOStatus, gen(IPOStatus_)
drop IPOStatus
rename IPOStatus_ IPOStatus

gen Total_Funding_Amount_K = Total_Funding_Amount/1000
gen Total_Funding_Amount_K_FirstVC = Total_Funding_Amount_FirstVC/1000

gen ln_Total_Funding_Amount = ln(Total_Funding_Amount)
gen ln_Total_Funding_Amount_FirstVC = ln(Total_Funding_Amount_FirstVC)

gen ln_NumberOfInvestors = ln(NumberOfInvestors)
***************
bysort VD_Backing: asdoc tab Industry2, sort

tab Revenue_Range if VD_Backing==0
tab Region2

**summary statistics for VD, VC, VCVD
asdoc 
tabstat TimeToFirst_VD TimeToFirst_VC TimeBetween_VCVD, s(mean median n)
bysort VD_Backing: tabstat TimeToFirst_VD TimeToFirst_VC TimeBetween_VCVD, s(mean median n)
***************
bysort VD_Backing: tab Revenue_Range, sort
tab VD_Backing
***************
**summary statistics for all var
***************
bysort VD_Backing: tabstat Total_Funding_Amount_FirstVC_K, s(mean sd min max) 
bysort VD_Backing: tabstat Founding_Year NumberOfEmployees_Range NumberOfFunding_Rounds NumberOfFunding_Rounds_FirstVC NumberOfInvestors Total_Funding_Amount_K Total_Funding_Amount_K_FirstVC VD_Backing TimeToFirst_VD TimeToFirst_VC TimeBetween_VCVD Region1 Region2 Revenue_Range Industry1 Industry2  ln_Total_Funding_Amount ln_Total_Funding_Amount_FirstVC   ln_NumberOfInvestors, s(N mean sd min max)

**industry classification
asdoc tab IndustryClassification, sort
**geographical distribution
* freq table
bysort VD_Backing: tab Region1, sort
asdoc tab Region1 if VD_Backing==.

* frequency graph
graph bar (count), over(Region1, sort(1) descending) 
graph bar (count) if VD_Backing==1, over(Region1, sort(1) descending) 
graph bar (count) if VD_Backing==., over(Region1, sort(1) descending) 


***************
**psm: Founding_Year, NumberOfFunding_Rounds_FirstVC, TimeToFirst_VC, Region2, Industry2, ln_Total_Funding_Amount_FirstVC
***************
*Covariate imbalance testing and graphing
global xlist1 Lastfundingdate Last_TimeToLastFunding NumberOfEmployees_Range NumberofFundingRounds Totalfundingamt ln_Totalfundingamt VD_TimeToFirst VC_TimeToFirst VCVD_TimeLapse Region2 Revenuerange


*t-test
*single

ttest Founding_Year, by(VD_Backing)

estpost ttest Founding_Year Industry2 NumberOfFunding_Rounds_FirstVC   ln_Total_Funding_Amount_FirstVC Region2 TimeToFirst_VC, by(VD_Backing)

*export diff table
esttab, wide nonumber mtitle("diff")
*export t-stat
foreach var of varlist Founding_Year Industry2 NumberOfFunding_Rounds_FirstVC   ln_Total_Funding_Amount_FirstVC Region2 TimeToFirst_VC {
   
     ttest `var', by(VD_Backing)
}


asdoc 
tab VD_Backing if _weight==1


***************************
*Exact Matching
***************************
egen groupyrind = group (Founding_Year Industry2 Region2)
logit VD_Backing i.Founding_Year ib4.Industry2 NumberOfFunding_Rounds_FirstVC ln_Total_Funding_Amount_FirstVC ib4.Region2 TimeToFirst_VC
predict double pscore if e(sample)
generate double pscore2 = groupyrind*10 + pscore
psmatch2 VD_Backing, n(1) noreplacement caliper(2) pscore(pscore2)

bysort VD_Backing: asdoc tab groupyrind
*1:1 Matching
***************************
tabstat _pscore, by(VD_Backing) stats (N mean median min max)
psmatch2 VD_Backing i.Founding_Year ib4.Industry2 NumberOfFunding_Rounds_FirstVC ln_Total_Funding_Amount_FirstVC ib4.Region2 TimeToFirst_VC, n(1) logit out(Total_EquityFunding_Amount) noreplacement
tab VD_Backing _weight

logit VD_Backing i.Founding_Year ib4.Industry2 NumberOfFunding_Rounds_FirstVC ln_Total_Funding_Amount_FirstVC ib4.Region2 TimeToFirst_VC
* create TABLE 6: this table needs to be create manually
asdoc 
pstest i.Founding_Year ib4.Industry2 NumberOfFunding_Rounds_FirstVC ln_Total_Funding_Amount_FirstVC ib4.Region2 TimeToFirst_VC, both label graph

pstest i.Founding_Year ib4.Industry2 NumberOfFunding_Rounds_FirstVC ln_Total_Funding_Amount_FirstVC ib4.Region2 TimeToFirst_VC, sum

psgraph
bysort VD_Backing: _weight
* before
twoway (kdensity _pscore if VD_Backing==1) (kdensity _pscore if VD_Backing==0, ///
lpattern(dash)), legend( label( 1 "treated") label( 2 "control" ) ) ///
xtitle("propensity scores before matching") name(before, replace)

* after
twoway (kdensity _pscore if VD_Backing==1 [aweight=_weight]) ///
(kdensity _pscore if VD_Backing==0 [aweight=_weight] ///
, lpattern(dash)), legend( label( 1 "treated") label( 2 "control" )) ///
xtitle("Propensity scores after matching") name(after, replace)

*after matching
ttest _pscore, by(VD_Backing)
ttest Founding_Year if _weight==1, by(VD_Backing)
Industry2 NumberOfFunding_Rounds_FirstVC ln_Total_Funding_Amount_FirstVC Region2 TimeToFirst_VC
ttest NumberOfEmployees_Range if _weight==1, by(VD_Backing)
estpost ttest Founding_Year Industry2 NumberOfFunding_Rounds_FirstVC ln_Total_Funding_Amount_FirstVC Region2 TimeToFirst_VC if _weight==1, by(VD_Backing)

*export diff table
esttab, wide nonumber mtitle("diff")
*export t-stat
foreach var of varlist Founding_Year Industry2 NumberOfFunding_Rounds_FirstVC ln_Total_Funding_Amount_FirstVC Region2 TimeToFirst_VC {
   
     ttest `var' if _weight==1, by(VD_Backing)
}

sum Founding_Year Industry2 NumberOfFunding_Rounds_FirstVC ln_Total_Funding_Amount_FirstVC Region2 TimeToFirst_VC if VD_Backing==0 & _weight==1
asdoc sum NumberOfFunding_Rounds_FirstVC NumberOfEmployees_Range ln_NumberOfInvestors ln_Total_Funding_Amount_FirstVC Region2 Revenue_Range TimeToFirst_VC if VD_Backing==0 & _weight==1

bysort VD_Backing: tab Revenue_Range if _weight==1










