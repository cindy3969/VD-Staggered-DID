Post-VD employees and revenue research
Retrieval date: 2026-10-15, Asia/Seoul

SCOPE AND STATUS
The target cohort is the 2,820 firms in table3_current_2820_cross_section_v2.dta.
The entire supplied pb_deal_finance.csv was processed for name matching.
Web research is INCOMPLETE. size_web_status explicitly distinguishes searched
firms from firms not yet searched. A blank is never evidence that a firm had
zero employees or zero revenue. See summary.json for current coverage counts.

MAIN VARIABLES
employees_t1, employees_t2, employees_t3: sourced point headcounts, including
explicit approximations with employees_basis_t# identifying the approximation.
employees_year_t#: actual measurement year. employees_date_t#: measurement
date when available, not the date we searched for the source.
employees_src_t#: public source URL. employees_basis_t#: source qualification.

revenue_t1, revenue_t2, revenue_t3: USD amounts, with source and basis in
revenue_src_t# and revenue_basis_t#. A public annual financial statement takes
precedence over a supplied PitchBook value. Management claims are flagged.
revenue_year_t#: measurement/fiscal year. A fiscal year ending in January 2018
is classified as 2018, not as calendar 2017.
revenue_date_t#: actual period end if publicly established. PitchBook deal dates
are not used as measurement dates and are retained in pb_rev_dealdate_t#.

All t# fields use observed year minus the target file's VDyear, including the
reference VDyear supplied for VD=0 firms. Only differences 1, 2, and 3 enter the
main wide variables. No past values are filled from current profile headcounts.
employees_nyears and revenue_nyears count nonmissing point observations.
No pooled cross-year mean, sum, or latest-year shortcut has been imposed.

PITCHBOOK UNITS AND LIMITATIONS
pb_revenue_raw_t#, pb_grossprofit_raw_t#, pb_netincome_raw_t#,
pb_ebitda_raw_t#, and pb_totaldebt_raw_t# retain the source numerical units.
Monetary values are strongly consistent with USD millions, based on checks:
  Instacart FY2022: source 2551, SEC USD 2,551 million.
  Instacart FY2021: source 1834, SEC USD 1,834 million.
  908 Devices FY2019: source 17.972, company annual report USD 17,972 thousand.
The main revenue_t# multiplies an accepted source value by 1,000,000.
This is an INFERENCE, not verification of the original export settings.
PitchBook supports configurable currency and scale, and this CSV includes
neither currency nor unit metadata. pb_unit_status records this limitation.
Sources:
https://pitchbook.com/help/pitchbook-excel-plugin-user-guide-mac-365
https://www.sec.gov/Archives/edgar/data/1579091/000119312523221345/d55348ds1.htm
https://s201.q4cdn.com/978897484/files/doc_financials/2020/q4/2020-10k-4Q.pdf

The supplied deal finance table does not identify whether each revenue record
is full-year, trailing-twelve-month, estimated, or another period. Fiscalyear
supports year assignment but does NOT prove that it is realized annual revenue.
The main basis field explicitly says 'period unverified' for these records.
For an annual-revenue-only analysis, use verified public annual figures or
resolve this period ambiguity first. Some source entries differ from annual
filings (e.g. 908 Devices FY2020), which is why public annual statements take
precedence. Do not call all main revenue values audited annual revenue.

MATCHING
First match a case-folded, whitespace-trimmed exact name when it maps to one
PitchBook company ID. Then consider unique alphanumeric-normalized names.
pb_name_match identifies these tiers. No fuzzy match is automatically accepted.
Lemonade/Le Monade, Meta View/Metaview, and R.e.d.d./REDD are explicitly withheld
as risky normalized matches. All matches are name-based; industry, location,
and historic ownership identity are not independently verified for every firm.
The supplied file has no such attributes to perform a full identity validation.

DUPLICATES AND CONFLICTS
Repeated deal rows do not create multiple firm-year observations. Values equal
after rounding the raw units to six decimals are treated as the same value.
Where distinct values remain within a firm/fiscalyear, the point value is left
missing unless a public source resolves it. No averaging or arbitrary latest
deal selection is used. pb_rev_nvals_t#, pb_rev_min_raw_t#,
pb_rev_max_raw_t#, and pb_rev_rows_t# expose the alternatives and source rows.
Source row numbers include the header (first data row is row 2).

SUPPLEMENTAL EMPLOYEE MEASURES
emp_est_t#: explicitly qualified third-party historical estimates.
emp_lower_t#: reported lower bounds such as 'more than 130'.
emp_upper_approx_t#: imprecise upper descriptions such as 'nearly 400'.
emp_fte_t#: full-time-equivalent counts, distinct from headcount.
emp_aux_year_t# and emp_aux_src_t# retain their measurement year and provenance.
These values are NOT silently inserted as exact employee headcounts.
web_observations.csv includes dates and notes for every source observation.
ARR, projected hires, customer employee counts, office-only counts, and values
outside the event window are not treated as the requested point measures.

SAMPLE ELIGIBILITY
The measurement collection retains all 2,820 requested firms. It has not applied
a new private-company filter. Some observations are from years in which a firm
became publicly listed or was acquired. Known cases are noted in the web audit.
Private-only regressions require time-specific IPO/acquisition screening.
The screenshot's sample counts (611 employees; 117 revenue) are not targets
and have not been artificially reproduced. Tables 8-10 have not been rerun.

AUDIT FILES
pb_matched_all_records.csv: all matched raw deal records and source row numbers,
including all supplied financial fields, regardless of event-window eligibility.
pb_window_records.csv: raw matches with fiscalyear in t+1 through t+3.
pb_conflicting_values.csv: differing values within a firm-year and metric.
pb_ambiguous_name_records.csv: unresolved one-name/multiple-ID cases.
pb_rejected_normalized_matches.csv: explicitly withheld normalized candidates.
pb_unmatched_firms.csv: target firms without an accepted source-name link.
web_observations.csv: public observations including excluded bounds and ARR.
postvd_size_firm_year.csv: 8,460 rows, one row per target firm and relative year.
legacy_size_unverified_audit.csv: prior local winsorization file overlaps.
The legacy file's employee dates cannot be inferred safely from lastdeal or
emp2025. Its potentially winsorized values are not used as new raw observations.

PRESERVATION AND CHECKS
Original files are backed up under backups/before_postvd_size_* before writes.
All original non-research columns, firm IDs, and row orders are preserved in
their respective CSV and DTA files. Existing Stata variable and value labels
are retained. Saved files are re-read to verify count and values, and every
main measurement year is checked against VDyear+t.
