VD replication package — Tables 1, 2 and Figure 1 (VD Table 20260928)

INPUT FILES (already provided by you in this chat)
  csdid_full7316_all_published_A1_applications_panel_1.csv   firm-year panel (7,316 firms)
  full_cohort_application_level_linked_through_2024.csv      application-level list  (code calls it app.csv)

DATA (this folder)
  data/application_level_list_through2024_used.csv
      40,458 unique applications (2,341 firms) used for the outcomes.
      Added columns: vd_backed, first_vd_year (next to firm name), grant_year_used,
      grant_lag_years, counted_in_granted_DV, in_analysis_window_le2024.
      Check: summing counted_in_granted_DV by firm x filing_year reproduces the panel's
      granted count in 100% of firm-years.
  data/firm_year_panel_analysis.csv
      88,547 firm-years (7,273 firms), founding year through 2024, used in every model.
      granted_apps_count = Table 1 DV; cite_mean = Table 2 DV;
      prior_patent_G, early_stage_G_reconstructed = subgroup flags.

CODE (Python 3; run in this order, all files in one folder)
  1. hist.py      builds the analysis panel: drops the 43 firms first treated in their
                  founding year, keeps years <= 2024, constructs prior_patent_G
                  (granted applications through G-1 > 0) and the early/late split.
  2. cite_var.py  adds forward-citation outcomes from the application list.
  3. dripw.py     Callaway-Sant'Anna estimator: never-treated controls; doubly robust
                  (logit propensity score + OLS outcome model) with ln(1+lagged funding),
                  lagged number of rounds, region FE, industry FE taken at the base
                  period; base g-1 for post cells, t-1 for pre cells; simple ATT and
                  mean of event-time ATTs at t=0..4; firm-level bootstrap.
                  Example: python3 dripw.py '[["all","ultimately_granted_filings","never",2024,true,49,7]]' out.csv
  4. run_boot.py  runs the 10 table cells (5 subgroups x 2 outcomes) with 49 bootstrap reps.
  5. fig1.py      Figure 1 (Panel A raw means + counterfactual, Panel B event study).

OUTPUT
  output/VD_Table1_2_Figure1_replication.docx   tables in publication format vs original
  output/replication_table1_table2_results.csv  all estimates, SEs, p-values, event-time ATTs
  output/figure1_data.csv, output/Figure1_replication.png
