from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(r"C:\Users\user\Documents\VD")
BASE_PANEL = ROOT / "outputs/csdid_replicated_from_rebuilt_patent_list/csdid_rebuilt_patent_panel.dta"
APPS = ROOT / "outputs/patent_application_list_rebuilt_2024_alias_test/patent_application_list_through_2024.csv"
OUT = ROOT / "outputs/csdid_replicated_from_rebuilt_patent_list/csdid_all_published_applications_panel.dta"
QA = ROOT / "outputs/csdid_replicated_from_rebuilt_patent_list/all_published_applications_QA.csv"

panel = pd.read_stata(BASE_PANEL, convert_categoricals=False)
apps = pd.read_csv(APPS, low_memory=False, dtype={"application_id": str})
apps["filing_year"] = pd.to_numeric(apps["filing_year"], errors="coerce")
apps = apps[apps["filing_year"].between(2010, 2024)].copy()

# Every unique published application is counted, irrespective of grant status.
annual = (apps.drop_duplicates(["full_firm_id", "application_id"])
          .groupby(["full_firm_id", "filing_year"])
          .size().rename("apps_all_published").reset_index()
          .rename(columns={"filing_year": "year"}))

panel = panel.drop(columns=[c for c in ["apps_all_published", "ln1p_apps_all_published"] if c in panel])
panel = panel.merge(annual, on=["full_firm_id", "year"], how="left", validate="one_to_one")
panel["apps_all_published"] = panel["apps_all_published"].fillna(0).astype(float)
panel["ln1p_apps_all_published"] = np.log1p(panel["apps_all_published"])
panel.to_stata(OUT, write_index=False, version=118)

z = apps[apps.organization_name.eq("24M Technologies")]
qa = pd.DataFrame({
    "metric": [
        "application_rows_2010_2024", "unique_applications_2010_2024",
        "firms_with_applications", "ultimately_granted", "not_yet_granted",
        "24M_applications", "24M_granted", "24M_not_yet_granted",
    ],
    "value": [
        len(apps), apps.application_id.nunique(), apps.full_firm_id.nunique(),
        int(apps.ultimately_granted.sum()), int((apps.ultimately_granted == 0).sum()),
        len(z), int(z.ultimately_granted.sum()), int((z.ultimately_granted == 0).sum()),
    ],
})
qa.to_csv(QA, index=False, encoding="utf-8-sig")
print(qa.to_string(index=False))
print(OUT)
