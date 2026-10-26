from pathlib import Path
import os
import re
import pandas as pd

ROOT = Path(r"C:\Users\user\Documents\VD\outputs\psm_final_2820_package")
APP = Path(r"C:\Users\user\Documents\VD\outputs\csdid_union_corrected_3yr\application_level_union_corrected_visible_mismatches.csv")
FULL = ROOT / "psm_stata_full7316_with_scores.dta"
MATCHED_DTA = ROOT / "psm_stata_matched_2820.dta"
MATCHED_CSV = ROOT / "psm_stata_matched_2820.csv"
AUDIT = ROOT / "replicated_appendix" / "patent_application_count_audit.csv"


def key(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


firms = pd.read_stata(FULL, convert_categoricals=False)
firms = firms.drop(columns=["patent_application_VD", "patent_application_win3", "name_key"], errors="ignore")
firms["name_key"] = firms["OrganizationName"].map(key)

apps = pd.read_csv(APP, low_memory=False)
apps = apps.loc[apps["filing_year"].between(2010, 2024)].copy()
apps = apps.drop_duplicates(["full_firm_id", "application_id"])
assert len(apps) == 39249
apps["name_key"] = apps["organization_name"].map(key)

reference = firms[["name_key", "VDYear"]].drop_duplicates().rename(columns={"VDYear": "reference_year"})
assert not reference["name_key"].duplicated().any(), "A duplicate firm name has conflicting reference years"
apps = apps.merge(reference, on="name_key", how="inner", validate="many_to_one")
apps["patent_application_VD"] = (apps["filing_year"] <= apps["reference_year"]).astype(int)
apps["patent_application_win3"] = apps["filing_year"].sub(apps["reference_year"]).between(0, 3).astype(int)
counts = apps.groupby("name_key", as_index=False)[["patent_application_VD", "patent_application_win3"]].sum()

firms = firms.merge(counts, on="name_key", how="left", validate="many_to_one")
firms[["patent_application_VD", "patent_application_win3"]] = firms[["patent_application_VD", "patent_application_win3"]].fillna(0).astype(int)

checks = firms.set_index("OrganizationName")
assert tuple(checks.loc["AliveCor", ["patent_application_VD", "patent_application_win3"]]) == (38, 16)
assert tuple(checks.loc["Health Outcomes Sciences", ["patent_application_VD", "patent_application_win3"]]) == (9, 0)

audit_cols = ["no", "OrganizationName", "VD_Backing", "Founding_Year", "VDYear", "Grant_VD", "Grant_3years", "patent_application_VD", "patent_application_win3", "matched_2820"]
firms[audit_cols].sort_values("OrganizationName").to_csv(AUDIT, index=False, encoding="utf-8-sig")

matched = firms.loc[firms["matched_2820"].eq(1)].copy()
assert len(matched) == 2820

for frame, target in [(firms, FULL), (matched, MATCHED_DTA)]:
    temp = target.with_suffix(".tmp.dta")
    frame.to_stata(temp, write_index=False, version=118)
    os.replace(temp, target)

temp_csv = MATCHED_CSV.with_suffix(".tmp.csv")
matched.to_csv(temp_csv, index=False, encoding="utf-8-sig")
try:
    os.replace(temp_csv, MATCHED_CSV)
except PermissionError:
    unlocked = ROOT / "psm_stata_matched_2820_corrected_applications.csv"
    os.replace(temp_csv, unlocked)
    print(f"The original CSV is locked; wrote corrected CSV to {unlocked}")

print(matched.groupby("VD_Backing")[["patent_application_VD", "patent_application_win3", "Grant_3years"]].agg(["count", "sum", "mean"]))
print(checks.loc[["AliveCor", "Health Outcomes Sciences"], ["VDYear", "Grant_VD", "Grant_3years", "patent_application_VD", "patent_application_win3"]])
