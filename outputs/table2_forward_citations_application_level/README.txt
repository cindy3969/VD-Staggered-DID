TABLE 2 FORWARD-CITATION REPLICATION

Primary method
- Unit: granted patent application.
- Citation cutoff: 2024.
- Right-truncation adjustment: raw forward citations / mean raw citations among linked granted applications in the same filing year.
- CPC/technology class: not used, following the project decision.
- Firm-year DV: mean adjusted citations across ultimately granted applications filed in the firm-year; zero when none.
- Estimator: Callaway-Sant'Anna doubly robust staggered DiD, never-treated controls, Table 1 controls/FE, 49 firm bootstrap replications.

Coverage
- Applications: 10,727
- Grant-linked applications: 6,319
- Recovered citation values: 5,801
- No recovered citation-link row, coded zero: 518

Files
- application_level_forward_citations_through_2024.csv: analysis-ready application-level citation data.
- citation_normalization_by_filing_year.csv: annual denominators.
- firm_year_panel_with_forward_citations.csv: estimation panel.
- Table_2_adjusted_forward_citation_results.csv: full point estimates, bootstrap SEs and p-values.
- table2_raw_sensitivity.csv: raw-citation point-estimate sensitivity analysis.
- Table_2_forward_citations_replication.docx: formatted table.
- dripw_table2.py: estimator.
- QA_summary.json: reproducibility checks.
