TABLE 2 FORWARD-CITATION REPLICATION — APPLICATION-LEVEL BUILD

Scope
- Focal input: application_level_list_through2024_used.csv (40,458 applications).
- Citation/CPC source: USPTO PatentsView final 2024 release.
- Analysis panel: verified 88,547-row Table 1 master firm-year panel (7,273 firms).
- Citation cutoff: 2024. Citation rows without dates are excluded. Citation links dated before the focal patent grant date are excluded.

Application-year grid
- Grant-linked applications: 36,050; linked grant patents: 36,085.
- Every grant-linked application is expanded from its filing year through 2024.
- Missing application-year citation counts are set to zero before cohort means are calculated.
- The normalization cohort is the full sample, not patents belonging to the focal firm.

Outcome definitions
1. fwd_raw: unique citing-patent links received in calendar year, summed across the firm's focal applications.
2. fwd_norm_cohort: application-year n_cites divided by the mean n_cites for the same filing-year x citation-year cohort; summed to firm-year.
3. fwd_norm_cohort_cpc: the same calculation with the denominator additionally split by primary current CPC3.
4. fwd_rate: for each application-year, cumulative citations through that year divided by observed post-grant years; summed to firm-year.
5. fwd_rate_norm: fwd_rate at application-year divided by the filing-year x citation-year mean; summed to firm-year.
6. fwd_rate_norm_cpc: rate normalization additionally split by primary CPC3.

Interpretation relative to the attached paper
- The paper defines adjusted citations by dividing a patent's citations by the mean for patents filed in the same year and three-digit technology class.
- fwd_norm_cohort_cpc applies that technology-cohort principle dynamically at filing-year x citation-year x CPC3, as requested.
- The non-CPC version is retained because the earlier project decision was not to require CPC splits; CPC versions are sensitivity checks.

Staggered DiD
- Estimator: Callaway-Sant'Anna csdid, DRIPW, never-treated controls.
- Treatment: first venture-debt year; same verified Table 1 master panel, controls, and subgroup definitions.
- Samples: all, no prior patent, prior patent, early stage, late stage.
- Results: Table2_all_truncation_methods_results.csv (30 specifications).
- Reproduction: MASTER_forward_citation_staggered_DiD.do contains the full serial workflow; run_one_forward_outcome.do is the parallelized outcome runner used for the completed estimates.

QA
- Valid dated post-grant citation links through 2024: 251,281.
- Application-year grid rows: 250,572.
- CPC coverage among grant-linked applications: 36,050 / 36,050.
- Correlation between the prior cumulative count and rebuilt post-grant total, on comparable applications: 0.9488.
- The rebuilt total is lower because pre-grant citations, missing-date rows, and duplicate cited-citing links are removed under the requested rules.
