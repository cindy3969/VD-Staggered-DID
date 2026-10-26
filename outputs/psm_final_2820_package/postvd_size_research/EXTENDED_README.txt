POST-VD SIZE EXTENSION — 2026-10-20 (Asia/Seoul)

STATUS: Partial web research. Original Table8 employee sample RECOVERED:
260122 winsorization_stage4.dta, emp2025_2, private==1 and
inrange(lastdeal2vd1,1,3). Exactly 611 firms; all five VD coefficients and
R-squared values reproduce. Original table is cross-sectional (one employee
value per firm), not a multi-year stacked firm-year regression.
Recovered sample and Stata commands: recovered_table8_original_611.dta and
REPLICATE_ORIGINAL_TABLE8.do. The Python audit uses a generalized inverse
for collinear FE columns; constants in models 2-5 depend on omitted-category
choices and differ from the screenshot. VD coefficients match all five.
The historical 117-revenue-observation sample is NOT yet reproduced.

LEGACY RESTORATION IN MASTER:
employees_legacy: original emp2025_2 matched by exact unique company name,
1,937 nonmissing firms (1,940 company matches, three missing employee values).
emp_legacy_table8: 353 current-cohort firms belonged to original611 sample.
emp_legacy_lastdeal, emp_legacy_t, emp_legacy_VDyear retain original timing.
The last-deal year is NOT verified as the employee observation year.
Do not assign legacy employees to t1-t3 or combine them with dated observations
until source timing is verified. The original and current2820 cohorts differ.
See legacy_employee_crosswalk.csv and legacy_recovery_summary.json.

The supplied matched PitchBook financial records were processed for ALL
available fiscal years strictly after VDyear. No arbitrary t<=3 cutoff.

MASTER DATA: table3_current_2820_cross_section_v2.dta and corresponding CSV.
All 2,820 firms and unrelated existing fields are preserved.

employees_post / revenue_post: EARLIEST available eligible post-VD-year point
observation, selected independently for each variable. Revenue is USD.
*_post_year: year of that observation. *_post_t: year minus VDyear.
*_post_src / *_post_basis / *_post_date: evidence and qualification.
*_post_nyears: number of available years across the expanded window.
These convenience fields are NOT pooled means, sums, or growth measures.
Employee and revenue observations for one company may be from different years.
Missing means unavailable, never zero. VD=0 uses the supplied reference VDyear.

employees_t1/t2/t3 and revenue_t1/t2/t3 remain restricted to t=1,2,3.
employees_nyears and revenue_nyears still count ONLY those three years.
The previous size_web_status and size_retrieved columns describe the earlier
2026-10-15 pass. They are not comprehensive progress records for this extension.

NEW FIRM-YEAR ANALYSIS (not the recovered original Table8):
Use postvd_size_all_years.dta (or .csv).
One record per observed firm-year, carrying the master covariates.
Outcome names: employees and revenue_usd. Timing: year and t.
Select inrange(t,1,3) to retain the original time window.
For the expanded analysis use t>=1, and change the table title accordingly.
Do not add headcounts across years. The same firm can contribute several rows.
Master wide-format size fields copied into this long file are reference fields;
the annual outcomes are ONLY employees and revenue_usd.

PRIVATE-FIRM RESTRICTION IS NOT APPLIED to collection or coverage counts.
The master status/status_year/status_date fields are retained for auditing.
Current status is not necessarily status on the measurement date. Some sources
are post-IPO or at acquisition, and need exclusion if the analysis requires
private firms at observation. Original Table8 selected private==1 and
lastdeal2vd1 in1..3 in its OLD cohort. Do not assume those old sample criteria
establish actual employee measurement dates in the current cohort.

SOURCE QUALIFICATIONS
PitchBook USD-million units remain INFERRED from prior public cross-checks,
not verified against export settings. Values are multiplied by 1e6 and marked
in basis. fiscalyear is used, not dealdate. Annual vs TTM vs estimate is not
established by that field. Conflicting company-year values are not averaged:
pb_all_years_revenue_conflicts.csv preserves them; point value remains missing
unless an eligible public observation is available.
Public reported/approximate point values take precedence over PitchBook.
current_website_snapshot means company-site staff count observed on retrieval
date (e.g. Databox2026); it is not assigned to an earlier historical year.
Explicit bounds, FTE, third-party estimates, ARR and TTM are preserved in
web_observations_extended.csv but not admitted to the point outcomes.
Full-time employee headcount is not FTE and is flagged in evidence notes.
Contractor/shopper counts and customer employee counts are not firm headcount.

web_observations_extended.csv retains all reviewed numeric web evidence,
including observations outside the post-VD period and ineligible metric types.
Use eligible_point and t to distinguish the included observations.
extended_summary.json gives coverage; all_firms_web_searched is false.

Example Stata inspection:
use "postvd_size_all_years.dta", clear
isid firm_id year
assert t == year - VDyear & t > 0
tab t if !missing(employees)
tab t if !missing(revenue_usd)
* Before estimation, define and document private-firm eligibility.
* keep if inrange(t,1,3)   // original window only

The older README.txt and summary.json document the earlier pass and are
historical; use this file and extended_summary.json for the extension.
