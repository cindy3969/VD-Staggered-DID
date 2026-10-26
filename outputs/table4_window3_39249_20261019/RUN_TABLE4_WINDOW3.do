version 19
clear all
set more off
global OUT "C:/Users/user/Documents/VD/outputs/table4_window3_39249_20261019"
capture log close
log using "$OUT/Table4.log", text replace
use "$OUT/firm_crosssection_window3.dta", clear
isid firm_id
assert _N==2820
* t = VDyear (existing pseudo-treatment year for non-VD firms).
* DV = ln(1 + sum of normalized citations for ultimately granted applications
* filed in t+1..t+3 / number of those applications). Citation cutoff: 2024.
* Zero eligible applications: outcome is set to zero, as in full-firm tables.
* Year FE is founding-year FE, consistent with the current Table 4 do-file.
* Annual normalization uses citing-patent grant dates, corrected 2026-10-19.
tempname H
postfile `H' str10 sample str10 method byte model str40 term double b se p N r2 using "$OUT/coefficients.dta", replace
foreach sample in complete full {
    preserve
    if "`sample'"=="complete" keep if complete_win3==1
    foreach method in cohort cpc {
        eststo clear
        forvalues j=1/4 {
            local interactions ""
            if inlist(`j',2,4) local interactions "VD_prior"
            if inlist(`j',3,4) local interactions "`interactions' VD_early"
            eststo m`j': reghdfe ln_quality_`method' VD `interactions' priorpatentdummy_VD earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)
            foreach term in VD `interactions' priorpatentdummy_VD earlystage ln_MoneyRaised_VD NumofFundingRounds_VD _cons {
                post `H' ("`sample'") ("`method'") (`j') ("`term'") (_b[`term']) (_se[`term']) (2*ttail(e(df_r),abs(_b[`term']/_se[`term']))) (e(N)) (e(r2))
            }
            estadd local RegionFE "Yes"
            estadd local IndustryFE "Yes"
            estadd local YearFE "Yes"
        }
        esttab m1 m2 m3 m4 using "$OUT/Table4_`method'_`sample'.rtf", replace rtf b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) order(VD VD_prior VD_early priorpatentdummy_VD earlystage ln_MoneyRaised_VD NumofFundingRounds_VD _cons) stats(RegionFE IndustryFE YearFE N r2, labels("Region FE" "Industry FE" "Founding-year FE" "Observations" "R-squared") fmt(%s %s %s 0 3)) title("Table 4. VD Backing and Post-VD Patent Quality: `method', `sample'") addnotes("p-values in parentheses; heteroskedasticity-robust standard errors." "Filing window t+1 to t+3; citations through 2024; ln(1+normalized citations per granted application)." "Complete: t<=2021. Full: includes incomplete 3-year windows.")
    }
    restore
}
postclose `H'
use "$OUT/coefficients.dta", clear
export delimited using "$OUT/coefficients.csv", replace
display "ALL_TABLE4_MODELS_COMPLETED"
log close
exit, clear
