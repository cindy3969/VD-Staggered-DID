version 19
clear all
set more off
capture log close
log using "C:/Users/user/Documents/VD/outputs/innovation_original2820_rebuild_20261020/stata_innovation_test.log", text replace
use "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_original_2820_cross_section_v2.dta", clear
replace priorpatentdummy_VD = 1 - patentdummybyfiling
replace Earlystage_VD = earlystage
global OUT "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_original2820_full_results"
capture mkdir "$OUT"
***Other innovation measures
* All variables below are reaggregated using ORIGINAL company and VDyear.
* Complete calendar window required; no-patent means/diversity are not zero.
* Status codes are labeled in the DTA. No blanket missing-to-zero replacement.
* breakthrough_win3 is a share, so fractional logit is used (not binary logit).
* cite_breadth_win3 is 0 for a patent with a verified empty reference list.
* New/old-domain counts require an observed, classified pre-reference portfolio.
tabstat nocite_win3 breakthrough_win3 desc_words_win3 fog_win3 ari_win3 ///
    neg_flesch_win3 figures_win3 sheets_win3 claims_win3 newpat_win3 oldpat_win3 ///
    newcpc_win3 cite_breadth_win3 self_citations_total_win3, ///
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

fracreg logit breakthrough_win3 VD i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear, vce(robust)
estimates store INNO_1
fracreg logit breakthrough_win3 i.VD##i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear, vce(robust)
estimates store INNO_2
fracreg logit breakthrough_win3 i.priorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear, vce(robust)
estimates store INNO_3
fracreg logit breakthrough_win3 i.VD##i.priorpatentdummy_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD ///
    i.Region2 i.Industry2 i.Foundingyear, vce(robust)
estimates store INNO_4
esttab INNO_1 INNO_2 INNO_3 INNO_4 using "$OUT/Other_innovation_measures.rtf", replace ///
    b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("(1)" "(2)" "(3)" "(4)") ///
    stats(N r2, labels("Observations" "R-squared")) ///
    title("DV: breakthrough_win3") ///
    addnotes("Original 2820-firm cohort; original controls and fixed effects." ///
    "Undefined or unobserved measurements remain missing; available N differs by DV." ///
    "p-values in parentheses. Breakthrough share uses fractional logit.")

*7-1
reghdfe ln_claims_win3 VD i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_5
reghdfe ln_claims_win3 i.VD##i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_6
reghdfe ln_claims_win3 i.priorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_7
reghdfe ln_claims_win3 i.VD##i.priorpatentdummy_VD ///
    i.VD##i.Earlystage_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_8
esttab INNO_5 INNO_6 INNO_7 INNO_8 using "$OUT/Other_innovation_measures.rtf", append ///
    b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("(1)" "(2)" "(3)" "(4)") ///
    stats(N r2, labels("Observations" "R-squared")) ///
    title("DV: ln_claims_win3") ///
    addnotes("Original 2820-firm cohort; original controls and fixed effects." ///
    "Undefined or unobserved measurements remain missing; available N differs by DV." ///
    "p-values in parentheses. Breakthrough share uses fractional logit.")

* Table A7: patent readability
*7-1
reghdfe gunning_fog_mean_win3 VD i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_9
reghdfe gunning_fog_mean_win3 i.VD##i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_10
reghdfe gunning_fog_mean_win3 i.priorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_11
reghdfe gunning_fog_mean_win3 i.VD##i.priorpatentdummy_VD ///
    i.VD##i.Earlystage_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_12
esttab INNO_9 INNO_10 INNO_11 INNO_12 using "$OUT/Other_innovation_measures.rtf", append ///
    b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("(1)" "(2)" "(3)" "(4)") ///
    stats(N r2, labels("Observations" "R-squared")) ///
    title("DV: gunning_fog_mean_win3") ///
    addnotes("Original 2820-firm cohort; original controls and fixed effects." ///
    "Undefined or unobserved measurements remain missing; available N differs by DV." ///
    "p-values in parentheses. Breakthrough share uses fractional logit.")

*7-2
reghdfe ari_mean_win3 VD i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_13
reghdfe ari_mean_win3 i.VD##i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_14
reghdfe ari_mean_win3 i.priorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_15
reghdfe ari_mean_win3 i.VD##i.priorpatentdummy_VD ///
    i.VD##i.Earlystage_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_16
esttab INNO_13 INNO_14 INNO_15 INNO_16 using "$OUT/Other_innovation_measures.rtf", append ///
    b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("(1)" "(2)" "(3)" "(4)") ///
    stats(N r2, labels("Observations" "R-squared")) ///
    title("DV: ari_mean_win3") ///
    addnotes("Original 2820-firm cohort; original controls and fixed effects." ///
    "Undefined or unobserved measurements remain missing; available N differs by DV." ///
    "p-values in parentheses. Breakthrough share uses fractional logit.")

*7-3
reghdfe neg_flesch_mean_win3 VD i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_17
reghdfe neg_flesch_mean_win3 i.VD##i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_18
reghdfe neg_flesch_mean_win3 i.priorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_19
reghdfe neg_flesch_mean_win3 i.VD##i.priorpatentdummy_VD ///
    i.VD##i.Earlystage_VD ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_20
esttab INNO_17 INNO_18 INNO_19 INNO_20 using "$OUT/Other_innovation_measures.rtf", append ///
    b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("(1)" "(2)" "(3)" "(4)") ///
    stats(N r2, labels("Observations" "R-squared")) ///
    title("DV: neg_flesch_mean_win3") ///
    addnotes("Original 2820-firm cohort; original controls and fixed effects." ///
    "Undefined or unobserved measurements remain missing; available N differs by DV." ///
    "p-values in parentheses. Breakthrough share uses fractional logit.")

****
*9-1
reghdfe ln_newpat_win3 VD i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_21
*9-1
reghdfe ln_newpat_win3 i.VD##i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_22
*9-1
reghdfe ln_newpat_win3 priorpatentdummy_VD VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_23
*9-1
reghdfe ln_newpat_win3 VD i.VD##i.priorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_24
esttab INNO_21 INNO_22 INNO_23 INNO_24 using "$OUT/Other_innovation_measures.rtf", append ///
    b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("(1)" "(2)" "(3)" "(4)") ///
    stats(N r2, labels("Observations" "R-squared")) ///
    title("DV: ln_newpat_win3") ///
    addnotes("Original 2820-firm cohort; original controls and fixed effects." ///
    "Undefined or unobserved measurements remain missing; available N differs by DV." ///
    "p-values in parentheses. Breakthrough share uses fractional logit.")

****
*9-2
reghdfe ln_oldpat_win3 VD i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_25
*9-1
reghdfe ln_oldpat_win3 i.VD##i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_26
*9-1
reghdfe ln_oldpat_win3 priorpatentdummy_VD VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_27
*9-1
reghdfe ln_oldpat_win3 VD i.VD##i.priorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_28
esttab INNO_25 INNO_26 INNO_27 INNO_28 using "$OUT/Other_innovation_measures.rtf", append ///
    b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("(1)" "(2)" "(3)" "(4)") ///
    stats(N r2, labels("Observations" "R-squared")) ///
    title("DV: ln_oldpat_win3") ///
    addnotes("Original 2820-firm cohort; original controls and fixed effects." ///
    "Undefined or unobserved measurements remain missing; available N differs by DV." ///
    "p-values in parentheses. Breakthrough share uses fractional logit.")

****
*9-2
reghdfe newcpc_win3 VD i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_29
*9-1
reghdfe newcpc_win3 i.VD##i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_30
*9-1
reghdfe newcpc_win3 priorpatentdummy_VD VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_31
*9-1
reghdfe newcpc_win3 VD i.VD##i.priorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_32
esttab INNO_29 INNO_30 INNO_31 INNO_32 using "$OUT/Other_innovation_measures.rtf", append ///
    b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("(1)" "(2)" "(3)" "(4)") ///
    stats(N r2, labels("Observations" "R-squared")) ///
    title("DV: newcpc_win3") ///
    addnotes("Original 2820-firm cohort; original controls and fixed effects." ///
    "Undefined or unobserved measurements remain missing; available N differs by DV." ///
    "p-values in parentheses. Breakthrough share uses fractional logit.")
	
****
capture drop ln_selfcitations_win3hare_win3
gen ln_selfcitations_win3hare_win3 = log(self_citations_total_win3+1)
sum originality_win3 cite_diversity_win3 cite_breadth_win3 selfcite_win3 self_citations_total_win3 selfshare_win3 generality_win3 
***
*10-1
reghdfe cite_breadth_win3 VD i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_33
*10-1
reghdfe cite_breadth_win3 i.VD##i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_34
*10-1
reghdfe cite_breadth_win3 priorpatentdummy_VD VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_35
*10-1
reghdfe cite_breadth_win3 VD i.VD##i.priorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_36
esttab INNO_33 INNO_34 INNO_35 INNO_36 using "$OUT/Other_innovation_measures.rtf", append ///
    b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("(1)" "(2)" "(3)" "(4)") ///
    stats(N r2, labels("Observations" "R-squared")) ///
    title("DV: cite_breadth_win3") ///
    addnotes("Original 2820-firm cohort; original controls and fixed effects." ///
    "Undefined or unobserved measurements remain missing; available N differs by DV." ///
    "p-values in parentheses. Breakthrough share uses fractional logit.")
	
*10-1
reghdfe ln_selfcitations_win3hare_win3 VD i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_37
*10-1
reghdfe ln_selfcitations_win3hare_win3 i.VD##i.priorpatentdummy_VD i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_38
*10-1
reghdfe ln_selfcitations_win3hare_win3 priorpatentdummy_VD VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_39
*10-1
reghdfe ln_selfcitations_win3hare_win3 VD i.VD##i.priorpatentdummy_VD i.VD##i.Earlystage_VD ///
    ln_MoneyRaised_VD NumofFundingRounds_VD, ///
    absorb(Region2 Industry2 Foundingyear) vce(robust)
estimates store INNO_40
esttab INNO_37 INNO_38 INNO_39 INNO_40 using "$OUT/Other_innovation_measures.rtf", append ///
    b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("(1)" "(2)" "(3)" "(4)") ///
    stats(N r2, labels("Observations" "R-squared")) ///
    title("DV: ln_selfcitations_win3hare_win3") ///
    addnotes("Original 2820-firm cohort; original controls and fixed effects." ///
    "Undefined or unobserved measurements remain missing; available N differs by DV." ///
    "p-values in parentheses. Breakthrough share uses fractional logit.")
	
********
*sum nocite_win3 breakthrough_win3 desc_words_win3 fog_win3 ari_win3 neg_flesch_win3 figures_win3 sheets_win3 claims_win3

*gen ln_desc_words_win3 = log(desc_words_win3+1)
*gen ln_figures_win3 = log(figures_win3+1)
*gen ln_sheets_win3 = log(sheets_win3+1)
*gen ln_claims_win3 = log(claims_win3+1)







display "INNOVATION_TEST_FINISHED"
log close
