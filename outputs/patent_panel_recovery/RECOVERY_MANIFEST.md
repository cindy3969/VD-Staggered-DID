# VD full-cohort patent panel recovery manifest

This manifest reconstructs the deleted full-cohort patent pipeline from the
VD project chat history. It deliberately excludes all BEEPS directories.

## Confirmed historical outputs

- Full sample: 7,316 firms.
- Firm-year panel: 96,400 rows (founding year through 2025).
- Linked published applications: 10,727 unique applications after alias updates.
- Ultimately granted applications: 6,319.
- Firms with an application link: 1,158.
- Patent outcomes were assigned to the official application filing year.
- The annual granted-application outcome was named `apps_ult_granted`.
- The main logged version was `ln1p_apps_ult_granted`.
- Forward citations were measured through 2024.
- The cited working paper defines truncation-adjusted citation as the focal
  patent's citations divided by the mean citations of patents in the same
  filing/application year and the same three-digit technology class.
- A later user instruction requested filing-year-only normalization. The
  restored data therefore retain both measures rather than overwriting either:
  `fw_cites_norm_year_class_2024` (paper-consistent) and
  `fw_cites_norm_year_2024` (filing-year-only primary specification).

## Historical build order

1. Build the 7,316-firm roster and treatment timing.
2. Link PatentsView pre-grant A1 publications to firms using normalized assignee
   names plus externally verified legal-name and alias additions.
3. Crosswalk A1 publications to granted patents.
4. Union the A1 application list with grant-only B1/B2 records mapped to their
   application IDs.
5. Deduplicate by application ID so an application is owned by only one sample
   firm.
6. Aggregate unique applications by `full_firm_id` and `filing_year`.
7. Merge annual outcomes into the full firm-year panel and construct treatment,
   event-time, controls, and H2/H3 moderators.
8. Count forward-citation edges for focal granted patents and normalize by the
   full-universe filing-year mean.

## Official PatentsView 2024 bulk inputs

Source record: https://zenodo.org/records/15783125

Quantity reconstruction requires at minimum:

- `g_application.tsv.zip`
- `g_patent.tsv.zip`
- `g_assignee_disambiguated.tsv.zip`
- `g_assignee_not_disambiguated.tsv.zip`

The A1/application-union reconstruction additionally uses:

- `pg_published_application.tsv.zip`
- `pg_assignee_disambiguated.tsv.zip`
- `pg_assignee_not_disambiguated.tsv.zip`
- `pg_granted_pgpubs_crosswalk.tsv.zip`

Forward-citation reconstruction additionally uses:

- `g_us_patent_citation.tsv.zip`

All archives are processed directly from ZIP streams; they should not be
expanded on disk.

## PSM reference-year definition

- Treated firms: actual first-VD year.
- Never-treated controls: founding year plus five.
- Updated patent covariate: cumulative number of unique applications filed on
  or before the reference year that were ultimately granted by the 2024
  snapshot.
- The inclusion of the reference year reproduces the historical matching
  convention and the earlier 2,820-firm update.

