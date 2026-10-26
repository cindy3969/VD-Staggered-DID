from pathlib import Path
import pandas as pd

ROOT = Path(r"C:\Users\user\Documents\VD")
SRC = ROOT / "outputs" / "csdid_union_corrected_3yr"
REF = ROOT / "outputs" / "claude_replication_reference" / "data"
OUT = ROOT / "outputs" / "csdid_all_applications_corrected"
OUT.mkdir(parents=True, exist_ok=True)

apps = pd.read_csv(SRC / "application_level_union_corrected_visible_mismatches.csv", low_memory=False)
panel = pd.read_csv(REF / "firm_year_panel_analysis.csv", low_memory=False)
apps["filing_year"] = pd.to_numeric(apps["filing_year"], errors="coerce")
apps = apps.loc[apps["filing_year"].between(2010, 2024)].copy()

# Application-number outcome: no restriction on eventual grant and no grant lag.
counts = (apps.drop_duplicates(["full_firm_id", "application_id"])
          .groupby(["full_firm_id", "filing_year"], as_index=False)
          .size().rename(columns={"filing_year": "year", "size": "applications_count"}))

# Requested same-title sensitivity: one firm-title invention, assigned to its
# earliest observed filing year. Blank titles remain application-specific keys.
inv = (apps.sort_values(["full_firm_id", "invention_key", "filing_year", "application_id"])
       .drop_duplicates(["full_firm_id", "invention_key"], keep="first"))
inv_counts = (inv.groupby(["full_firm_id", "filing_year"], as_index=False)
              .size().rename(columns={"filing_year": "year", "size": "applications_title_dedup"}))

p = panel.copy()
p["G"] = p["first_vd_year_G"].fillna(0).astype(int)
p["prior"] = p["prior_patent_G"]
p["early"] = p["early_stage_G_reconstructed"]
p = p.merge(counts, on=["full_firm_id", "year"], how="left")
p = p.merge(inv_counts, on=["full_firm_id", "year"], how="left")
p[["applications_count", "applications_title_dedup"]] = p[["applications_count", "applications_title_dedup"]].fillna(0)

p.to_csv(OUT / "hist_panel.csv", index=False)
p.to_stata(OUT / "firm_year_all_applications_corrected.dta", write_index=False, version=118)
inv.to_csv(OUT / "application_level_title_deduplicated.csv", index=False)
pd.DataFrame({
    "item": ["application_rows_2010_2024", "unique_firm_application_pairs",
             "title_deduplicated_inventions", "panel_observations", "panel_firms"],
    "value": [len(apps), len(apps.drop_duplicates(["full_firm_id", "application_id"])),
              len(inv), len(p), p.full_firm_id.nunique()],
}).to_csv(OUT / "construction_QA.csv", index=False)
print(pd.read_csv(OUT / "construction_QA.csv").to_string(index=False))
