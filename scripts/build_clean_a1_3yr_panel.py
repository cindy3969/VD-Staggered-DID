from pathlib import Path
import pandas as pd
import re

ROOT = Path(r"C:\Users\user\Documents\VD")
REF = ROOT / "outputs" / "claude_replication_reference"
OUT = ROOT / "outputs" / "csdid_a1_clean_3yr"
OUT.mkdir(parents=True, exist_ok=True)

# Read the union only for exclusion accounting. The analytic patent universe is
# the separately rebuilt 10,727-row A1 publication file, which also contains titles.
union_apps = pd.read_csv(REF / "data" / "application_level_list_through2024_used.csv", low_memory=False)
apps = pd.read_csv(
    ROOT / "outputs" / "patent_application_list_rebuilt_2024" /
    "patent_application_list_through_2024.csv", low_memory=False
)
panel = pd.read_csv(REF / "data" / "firm_year_panel_analysis.csv", low_memory=False)

# Strict filing-time universe: discard every grant-derived record lacking an A1
# publication. This is stronger than excluding only the flagged review list and
# therefore removes all 29,731 grant-only candidates, including its risky matches.
a1 = apps.copy()
a1["filing_date"] = pd.to_datetime(a1["filing_date"], errors="coerce")
a1["first_grant_date"] = pd.to_datetime(a1["first_grant_date"], errors="coerce")
a1["grant_days"] = (a1["first_grant_date"] - a1["filing_date"]).dt.days
a1["granted_within_3y"] = (
    a1["ultimately_granted"].eq(1)
    & a1["grant_days"].between(0, 365.25 * 3, inclusive="both")
).astype(int)

# A second, stricter unit of observation treats identical normalized titles
# within a firm as one invention. Blank titles are never merged.
def norm_title(value):
    if pd.isna(value) or not str(value).strip():
        return ""
    return " ".join(re.findall(r"[a-z0-9]+", str(value).casefold()))

a1["title_normalized"] = a1["patent_title"].map(norm_title)
a1["invention_key"] = a1["title_normalized"]
blank = a1["invention_key"].eq("")
a1.loc[blank, "invention_key"] = "application:" + a1.loc[blank, "application_id"].astype(str)

duplicate_audit = a1.loc[a1.duplicated(["full_firm_id", "invention_key"], keep=False)].copy()
duplicate_audit = duplicate_audit.sort_values(
    ["full_firm_id", "invention_key", "filing_date", "application_id"]
)
duplicate_audit.to_csv(OUT / "same_title_application_duplicate_audit.csv", index=False)

def join_ids(s):
    return "|".join(sorted(set(s.dropna().astype(str))))

inventions = (a1.groupby(["full_firm_id", "invention_key"], as_index=False)
    .agg(
        organization_name=("organization_name", "first"),
        patent_title=("patent_title", "first"),
        title_normalized=("title_normalized", "first"),
        representative_filing_date=("filing_date", "min"),
        earliest_grant_date=("first_grant_date", "min"),
        member_application_ids=("application_id", join_ids),
        application_count_same_title=("application_id", "nunique"),
    ))
inventions["filing_year"] = inventions["representative_filing_date"].dt.year
inventions["grant_days_from_first_filing"] = (
    inventions["earliest_grant_date"] - inventions["representative_filing_date"]
).dt.days
inventions["granted_within_3y"] = inventions["grant_days_from_first_filing"].between(
    0, 365.25 * 3, inclusive="both"
).astype(int)
inventions.to_csv(OUT / "A1_title_deduplicated_inventions_all_years.csv", index=False)

# Every retained filing cohort receives the same complete 3-year follow-up by
# the 2024-12-31 snapshot, so 2021 is the last admissible filing year.
a1_mature = a1.loc[a1["filing_year"].le(2021)].copy()
counts = (a1_mature.groupby(["full_firm_id", "filing_year"], as_index=False)
          ["granted_within_3y"].sum()
          .rename(columns={"filing_year": "year", "granted_within_3y": "granted_3yr_a1"}))

inv_mature = inventions.loc[inventions["filing_year"].le(2021)].copy()
inv_counts = (inv_mature.groupby(["full_firm_id", "filing_year"], as_index=False)
              ["granted_within_3y"].sum()
              .rename(columns={"filing_year": "year",
                               "granted_within_3y": "granted_3yr_a1_title_dedup"}))

p = panel.loc[panel["year"].le(2021)].copy()
p["prior_original"] = p["prior_patent_G"]
p = p.merge(counts, on=["full_firm_id", "year"], how="left")
p = p.merge(inv_counts, on=["full_firm_id", "year"], how="left")
p["granted_3yr_a1"] = p["granted_3yr_a1"].fillna(0).astype(float)
p["granted_3yr_a1_title_dedup"] = p["granted_3yr_a1_title_dedup"].fillna(0).astype(float)
p["G"] = p["first_vd_year_G"].fillna(0).astype(int)
p["early"] = p["early_stage_G_reconstructed"]

# Recompute prior technological assets from the cleaned outcome through G-1.
cum = p.sort_values(["full_firm_id", "year"]).copy()
cum["clean_cum"] = cum.groupby("full_firm_id")["granted_3yr_a1"].cumsum()
base = cum.loc[cum["year"].eq(cum["G"] - 1), ["full_firm_id", "clean_cum"]]
base = base.drop_duplicates("full_firm_id").assign(prior=lambda d: (d.clean_cum > 0).astype(int))
p = p.drop(columns=["prior_patent_G"], errors="ignore").merge(
    base[["full_firm_id", "prior"]], on="full_firm_id", how="left"
)

p.to_csv(OUT / "hist_panel.csv", index=False)
p.to_stata(OUT / "csdid_A1_only_granted_within3y_panel.dta", write_index=False, version=118)
a1_mature.to_csv(OUT / "A1_applications_mature_3yr_audit.csv", index=False)

qa = pd.DataFrame({
    "item": [
        "original_union_applications", "excluded_grant_only_applications",
        "A1_applications_all_years", "A1_applications_filed_through_2021",
        "A1_applications_granted_within_3y", "analysis_panel_observations",
        "analysis_panel_firms", "same_title_duplicate_application_rows",
        "title_deduplicated_inventions_through_2021",
        "title_deduplicated_inventions_granted_within_3y",
    ],
    "value": [
        len(union_apps), union_apps["source_has_A1_publication"].eq(0).sum(), len(a1),
        len(a1_mature), a1_mature["granted_within_3y"].sum(), len(p),
        p["full_firm_id"].nunique(), len(duplicate_audit), len(inv_mature),
        inv_mature["granted_within_3y"].sum(),
    ],
})
qa.to_csv(OUT / "cleaning_QA.csv", index=False)
print(qa.to_string(index=False))
