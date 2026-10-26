from pathlib import Path
import pandas as pd


ROOT = Path(r"C:\Users\user\Documents\VD")
SRC = ROOT / "outputs" / "claude_replication_reference" / "data"
OUT = ROOT / "outputs" / "csdid_historical_replication_verified"
OUT.mkdir(parents=True, exist_ok=True)


panel = pd.read_csv(SRC / "firm_year_panel_analysis.csv")

# Stata-facing aliases preserve the empirically recovered definitions.
panel = panel.rename(
    columns={
        "first_vd_year_G": "g_first_vd",
        "granted_apps_count": "apps_ult_granted",
        "prior_patent_G": "prior_patent_vd",
        "early_stage_G_reconstructed": "early_stage_vd",
    }
)
panel["apps_ult_granted"] = panel["apps_ult_granted"].fillna(0).astype(float)
panel["ln1p_apps_ult_granted"] = panel["apps_ult_granted"].map(lambda x: __import__("math").log1p(x))
panel["event_time"] = panel["year"] - panel["g_first_vd"]
panel.loc[panel["g_first_vd"].eq(0), "event_time"] = pd.NA

# Stata cannot export object columns containing mixed missing values reliably.
for col in panel.select_dtypes(include="object"):
    panel[col] = panel[col].fillna("").astype(str)

panel.to_stata(
    OUT / "MASTER_CS_TABLE_restored.dta",
    write_index=False,
    version=118,
    variable_labels={
        "apps_ult_granted": "Ultimately granted applications filed in firm-year (raw count)",
        "g_first_vd": "First VD year; 0 for never treated",
        "prior_patent_vd": "Any ultimately granted filing before first VD year",
        "early_stage_vd": "Early-stage indicator at first VD (reconstructed)",
    },
)

apps = pd.read_csv(SRC / "application_level_list_through2024_used.csv", low_memory=False)
for col in apps.select_dtypes(include="object"):
    apps[col] = apps[col].fillna("").astype(str)
apps.to_stata(
    OUT / "application_level_list_through2024_restored.dta",
    write_index=False,
    version=118,
)

checks = pd.DataFrame(
    {
        "check": [
            "panel_observations",
            "panel_firms",
            "treated_firms",
            "never_treated_firms",
            "application_rows",
            "unique_applications",
            "application_firms",
        ],
        "value": [
            len(panel),
            panel.full_firm_id.nunique(),
            panel.loc[panel.g_first_vd.gt(0), "full_firm_id"].nunique(),
            panel.loc[panel.g_first_vd.eq(0), "full_firm_id"].nunique(),
            len(apps),
            apps.application_id.nunique(),
            apps.full_firm_id.nunique(),
        ],
    }
)
checks.to_csv(OUT / "restoration_checks.csv", index=False)
print(checks.to_string(index=False))
