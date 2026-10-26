from pathlib import Path
import pandas as pd

ROOT = Path(r"C:\Users\user\Documents\VD")
SRC = ROOT / "outputs" / "csdid_union_corrected_3yr"
REF = ROOT / "outputs" / "claude_replication_reference" / "data"
OUT = ROOT / "outputs" / "csdid_all_applications_corrected"

apps = pd.read_csv(SRC / "application_level_union_corrected_visible_mismatches.csv", low_memory=False)
panel = pd.read_csv(REF / "firm_year_panel_analysis.csv", low_memory=False)
apps["filing_year"] = pd.to_numeric(apps["filing_year"], errors="coerce")
apps["grant_lag_years"] = pd.to_numeric(apps["grant_lag_years"], errors="coerce")
apps["ultimately_granted"] = pd.to_numeric(apps["ultimately_granted"], errors="coerce").fillna(0)
apps = apps.loc[apps["filing_year"].between(2010, 2024)].drop_duplicates(
    ["full_firm_id", "application_id"]
).copy()

apps["apps_all"] = 1
apps["ug_naive_2024"] = apps["ultimately_granted"].eq(1).astype(int)
apps["ug_within2y"] = (apps["ultimately_granted"].eq(1) & apps["grant_lag_years"].between(0, 2)).astype(int)
apps["ug_within3y"] = (apps["ultimately_granted"].eq(1) & apps["grant_lag_years"].between(0, 3)).astype(int)
apps["ug_within5y"] = (apps["ultimately_granted"].eq(1) & apps["grant_lag_years"].between(0, 5)).astype(int)

outcomes = ["apps_all", "ug_naive_2024", "ug_within2y", "ug_within3y", "ug_within5y"]
annual = apps.groupby(["full_firm_id", "filing_year"], as_index=False)[outcomes].sum()
annual = annual.rename(columns={"filing_year": "year"})

p = panel.merge(annual, on=["full_firm_id", "year"], how="left")
p[outcomes] = p[outcomes].fillna(0).astype(float)
# This outcome has no grant-lag restriction; the do-file restricts the panel to
# filing years <=2020, guaranteeing at least four years of grant follow-up.
p["ug_mature2020"] = p["ug_naive_2024"]
p["G"] = p["first_vd_year_G"].fillna(0).astype(int)
p["prior"] = p["prior_patent_G"]
p["early"] = p["early_stage_G_reconstructed"]

p.to_stata(OUT / "firm_year_all_applications_and_truncation_specs.dta", write_index=False, version=118)
p.to_csv(OUT / "firm_year_all_applications_and_truncation_specs.csv", index=False)

qa = pd.DataFrame({
    "specification": ["all applications", "naive ultimately granted through 2024",
                      "granted within 2 years", "granted within 3 years",
                      "granted within 5 years"],
    "application_count": [apps[x].sum() for x in outcomes],
    "last_complete_filing_year": [2024, 2024, 2022, 2021, 2019],
})
qa.to_csv(OUT / "combined_outcome_QA.csv", index=False)
print(qa.to_string(index=False))
