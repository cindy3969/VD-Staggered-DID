# Table 2 forward-citation replication — corrected 39,249 applications

This rebuild uses the corrected application-level union, not the Downloads file.

## Analysis universe

- Original union: 40,458 applications
- Confirmed mismatches removed: 737
- Corrected union: 39,721 applications
- Filing years 2010–2024, unique `full_firm_id × application_id`: **39,249**
- Grant-linked applications: 34,855
- Dated, valid, post-grant forward-citation links: 199,187
- Complete application-year grid rows: 228,445
- Final firm-year panel: 88,547 rows and 7,273 firms
- Citation observation cutoff: 2024

## Outcomes

- `fwd_raw`: calendar-year citations, summed to firm-year.
- `fwd_norm_cohort`: application-year citations divided by the filing-year × citation-year cohort mean, including zero-citation application-years, then summed to firm-year.
- `fwd_norm_cohort_cpc`: the same normalization within filing-year × citation-year × primary CPC3 cells.
- `fwd_rate`: cumulative citations divided by observed post-grant exposure years, summed to firm-year.
- `fwd_rate_norm`: exposure-adjusted rate normalized by filing-year × citation-year cohort.
- `fwd_rate_norm_cpc`: exposure-adjusted rate normalized within filing-year × citation-year × primary CPC3 cells.

Citation rows dated before the focal patent's grant date or without a citation date are excluded. CPC variants are provided as robustness checks; the non-CPC filing-cohort measure remains the main requested normalization.

## Main files

- `firm_year_with_citations.csv` / `.dta`: full analysis panel.
- `application_citation_year_grid.csv`: zero-complete application-year construction grid.
- `application_level_with_forward_citation_methods.csv`: application-level measures.
- `Table2_all_truncation_methods_results.csv`: all six outcomes × five analysis samples.
- `Table2_forward_citation_results.xlsx`: formatted results, methods/QA, and a panel preview.
- `MASTER_forward_citation_staggered_DiD.do`: reproducible Stata master script.
- `QA_summary.json`: machine-readable construction checks.
