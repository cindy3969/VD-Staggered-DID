PSM FINAL 2,820 PACKAGE
=======================

1. ORIGINAL_PSM_20240117.do
   Historical do-file containing the original psmatch2 specification.
   Its opening input file, "20240117_2010 to 2015 firms.dta", is no longer present,
   so this historical code is not currently standalone-runnable.

2. ORIGINAL_final_matched_2820.dta
   Authoritative legacy matched analysis file: 1,410 VD-treated and 1,410 controls.
   Warning: Dermira and Eargo remain coded as treated in this historical file.

3. ORIGINAL_build_cross_section_2820.do
   Historical downstream construction code that attached patent, funding, and
   other analysis variables to the matched sample.

4. REBUILT_PSM_1410_and_diagnostics.do
   Standalone-runnable rebuilt PSM and diagnostic code using the surviving
   7,316-firm treatment/control reconstruction. Dermira and Eargo are controls.
   Thirty otherwise VD-backed firms are excluded from the propensity-score
   estimation because reference-year funding amount is missing.

5. REBUILT_corrected_matched_2820.dta
   Rebuilt matched sample: 1,410 corrected VD-treated and 1,410 controls.
   Its membership differs from the historical file: Dermira/Eargo are excluded
   as treated, while Cortex/Nomi1 are eligible under the rebuilt specification.

Supporting diagnostics are in:
C:/Users/user/Documents/VD/outputs/psm_rematch_rebuilt

Firm-level inclusion/exclusion audit is in:
C:/Users/user/Documents/VD/outputs/full_cohort_treatment_audit/vd_1442_to_1410_firm_audit.dta
