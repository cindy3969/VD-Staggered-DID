version 17
clear all
local project "C:/Users/user/Documents/VD"
use "`project'/outputs/psm_final_2820_package/table3_current_2820_cross_section_v2.dta", clear
isid firm_id
assert _N == 2820
merge 1:1 firm_id using "`project'/outputs/vd_lender_validation_2820/firm_validation_2820.dta", ///
    keepusing(debt_candidate_n cb_debt_n named_deal_n anonymous_deal_n any_named only_anonymous ///
    first_named first_source_n firm_category first_category strict_lender_support first_lender_support ///
    strict_context_support first_context_support government_review type_conflict year_mismatch ///
    ipo_before_deal anon_prior_series anon_seed_or_same_day first_prior_series first_amount_reported ///
    first_date_reported validation_group external_noncore_review) assert(match) nogen
label define lender_cat 0 "Identity absent / no candidate deal" 1 "Specialized venture debt" ///
    2 "Venture/startup lending bank" 3 "Other institutional" 4 "Ambiguous", replace
label values firm_category first_category lender_cat
assert _N == 2820
* Never recode VD=0 because lender identity is missing.
* This creates a separate file and preserves the original analysis dataset.
save "`project'/outputs/vd_lender_validation_2820/table3_2820_with_validation_flags.dta", replace
