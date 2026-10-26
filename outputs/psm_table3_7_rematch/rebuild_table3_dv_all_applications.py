from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\user\Documents\VD")
OUT = ROOT / "outputs" / "psm_table3_7_rematch"
UNION = ROOT / "outputs" / "csdid_union_corrected_3yr" / "application_level_union_corrected_visible_mismatches.csv"

# Corrected application-level union: 40,458 original rows - 737 confirmed bad links.
apps = pd.read_csv(UNION, low_memory=False)
apps["filing_year"] = pd.to_numeric(apps["filing_year"], errors="coerce")
apps = apps.loc[apps.filing_year.between(2010, 2024)].copy()
apps = apps.drop_duplicates(["full_firm_id", "application_id"])
assert len(apps) == 39249, f"Expected 39,249 unique firm-application rows, found {len(apps):,}"
universe_n = len(apps)

cross = pd.read_stata(OUT / "rematched_2820_cross_section.dta", convert_categoricals=False)
refs = cross[["firm_id", "VDyear"]].rename(columns={"firm_id": "full_firm_id", "VDyear": "reference_year"})
apps = apps.merge(refs, on="full_firm_id", how="inner", validate="many_to_one")
apps["relative_year"] = apps.filing_year - apps.reference_year

# Window 3 means filing years t+1, t+2, and t+3. No ultimately-granted restriction.
w3 = apps.loc[apps.relative_year.between(1, 3)]
counts = w3.groupby("full_firm_id")["application_id"].nunique()
cross["patentbyfiling_win3"] = cross.firm_id.map(counts).fillna(0).astype(int)
cross["ln_patentbyfiling_win3"] = np.log1p(cross.patentbyfiling_win3)

cross.to_stata(OUT / "rematched_2820_cross_section.dta", write_index=False, version=118)
cross.to_csv(OUT / "rematched_2820_cross_section.csv", index=False, encoding="utf-8-sig")

summary = pd.DataFrame({
    "metric": [
        "corrected_union_rows", "unique_firm_application_2010_2024",
        "matched_sample_window3_applications", "firms_with_window3_application",
        "firms_with_zero_window3_applications", "mean_log1p_window3_applications",
    ],
    "value": [
        39721, universe_n,
        int(cross.patentbyfiling_win3.sum()), int((cross.patentbyfiling_win3 > 0).sum()),
        int((cross.patentbyfiling_win3 == 0).sum()), float(cross.ln_patentbyfiling_win3.mean()),
    ],
})
summary.to_csv(OUT / "Table3_DV_all_applications_QA.csv", index=False, encoding="utf-8-sig")
print(summary.to_string(index=False))
