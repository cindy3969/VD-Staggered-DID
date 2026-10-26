"""Rebuild the 7,316-firm treatment audit from surviving source files."""
from pathlib import Path
import re
import numpy as np
import pandas as pd

ROOT = Path(r"C:/Users/user/Documents/VD")
OUT = ROOT / "outputs/full_cohort_treatment_audit"
OUT.mkdir(parents=True, exist_ok=True)
XLSX = Path(r"C:/Users/user/iCloudDrive/5학기/연구미팅/데이터/2010 2015 Crunchbase deals merged_v4.xlsx")
LEGACY = Path(r"C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms/240626.dta")


def key(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


deals = pd.read_excel(XLSX, header=1)
deals = deals.sort_values(["Organization Name", "deal no"], kind="stable")
firm = deals.drop_duplicates("Organization Name", keep="first").copy()
assert len(firm) == 7316
firm["name_key"] = firm["Organization Name"].map(key)
firm["vd_backed_v4_raw"] = pd.to_numeric(firm["VD_Backing"], errors="coerce").fillna(0).astype("int8")
firm["vd_backed_v4_corrected"] = firm["vd_backed_v4_raw"]
firm.loc[firm["Organization Name"].isin(["Dermira", "Eargo"]), "vd_backed_v4_corrected"] = 0

# First-VD year is stored on the firm row in the source workbook's VD Year field.
firm["first_vd_year_v4"] = pd.to_numeric(firm["VD Year"], errors="coerce")
firm.loc[firm["vd_backed_v4_corrected"].eq(0), "first_vd_year_v4"] = np.nan

legacy = pd.read_stata(LEGACY, convert_categoricals=False)
legacy["name_key"] = legacy["OrganizationName"].map(key)
legacy = legacy.drop_duplicates("name_key", keep="first")
legacy["vd_backed_legacy_raw"] = pd.to_numeric(legacy["VD_Backing"], errors="coerce")
legacy["vd_backed_legacy_corrected"] = legacy["vd_backed_legacy_raw"]
legacy.loc[legacy["OrganizationName"].isin(["Dermira", "Eargo"]), "vd_backed_legacy_corrected"] = 0

keep_legacy = legacy[[
    "name_key", "OrganizationName", "vd_backed_legacy_raw",
    "vd_backed_legacy_corrected", "VD_Year", "Founding_Year",
    "TimeToFirst_VC", "NumberOfFunding_Rounds_FirstVD",
    "ln_Total_Funding_Amount_FirstVD", "Industry2", "Region2", "Patents_VD"
]].rename(columns={
    "OrganizationName": "legacy_organization_name",
    "VD_Year": "first_vd_year_legacy",
    "Founding_Year": "founding_year_legacy",
    "TimeToFirst_VC": "time_first_vc_legacy",
    "NumberOfFunding_Rounds_FirstVD": "funding_rounds_ref_legacy",
    "ln_Total_Funding_Amount_FirstVD": "ln_funding_ref_legacy",
    "Industry2": "industry2_legacy",
    "Region2": "region2_legacy",
    "Patents_VD": "patents_vd_legacy",
})

audit = firm.merge(
    keep_legacy,
    left_on="Organization Name",
    right_on="legacy_organization_name",
    how="left",
    validate="one_to_one",
    suffixes=("", "_legacy_key"),
)
audit.insert(0, "full_firm_id", np.arange(1, len(audit) + 1, dtype=np.int32))
audit["treatment_definition_disagrees"] = (
    audit["vd_backed_v4_corrected"].ne(audit["vd_backed_legacy_corrected"])
    & audit["vd_backed_legacy_corrected"].notna()
).astype("int8")
audit["treatment_note"] = ""
audit.loc[audit["Organization Name"].eq("Dermira"), "treatment_note"] = "User-verified recode from VD to non-VD"
audit.loc[audit["Organization Name"].eq("Eargo"), "treatment_note"] = "User-verified recode from VD to non-VD"
audit.loc[audit["Organization Name"].eq("Yosi Health"), "treatment_note"] = (
    "Legacy Stata definition=VD; merged_v4 definition=non-VD; requires adjudication"
)
audit.loc[audit["vd_backed_legacy_corrected"].isna(), "treatment_note"] = (
    "No normalized-name match in legacy 240626 file"
)

cols = [
    "full_firm_id", "Organization Name", "found year", "name_key",
    "vd_backed_v4_raw", "vd_backed_v4_corrected", "first_vd_year_v4",
    "vd_backed_legacy_raw", "vd_backed_legacy_corrected", "first_vd_year_legacy",
    "treatment_definition_disagrees", "treatment_note"
]
audit = audit[cols].rename(columns={"Organization Name": "organization_name", "found year": "founding_year"})
for string_col in ["organization_name", "name_key", "treatment_note"]:
    audit[string_col] = audit[string_col].fillna("").astype(str)

audit.to_stata(OUT / "full_cohort_treatment_definition_7316.dta", write_index=False, version=118)
audit.to_csv(OUT / "full_cohort_treatment_definition_7316.csv", index=False, encoding="utf-8-sig")

# Reconstructed firm-level analysis input. This restores the treatment/control
# definition and PSM covariates, but it is not the deleted patent-year outcome panel.
analysis = firm.merge(
    keep_legacy,
    left_on="Organization Name",
    right_on="legacy_organization_name",
    how="left",
    validate="one_to_one",
    suffixes=("", "_legacy_key"),
)
analysis.insert(0, "full_firm_id", np.arange(1, len(analysis) + 1, dtype=np.int32))
analysis["organization_name"] = analysis["Organization Name"].fillna("").astype(str)
analysis["founding_year"] = pd.to_numeric(analysis["found year"], errors="coerce")
analysis["vd_backed"] = analysis["vd_backed_legacy_corrected"].where(
    analysis["vd_backed_legacy_corrected"].notna(), analysis["vd_backed_v4_corrected"]
).astype("int8")
analysis["first_vd_year"] = pd.to_numeric(analysis["first_vd_year_legacy"], errors="coerce")
analysis.loc[analysis.vd_backed.eq(0), "first_vd_year"] = np.nan
analysis["g_first_vd"] = analysis["first_vd_year"].fillna(0)
analysis["time_first_vc"] = pd.to_numeric(analysis["time_first_vc_legacy"], errors="coerce")
analysis["first_vc_year"] = analysis["founding_year"] + analysis["time_first_vc"]
analysis["funding_rounds_ref"] = pd.to_numeric(analysis["funding_rounds_ref_legacy"], errors="coerce")
analysis["ln_funding_ref"] = pd.to_numeric(analysis["ln_funding_ref_legacy"], errors="coerce")
analysis["industry2"] = pd.to_numeric(analysis["industry2_legacy"], errors="coerce")
analysis["region2"] = pd.to_numeric(analysis["region2_legacy"], errors="coerce")
analysis["prior_patent"] = (pd.to_numeric(analysis["patents_vd_legacy"], errors="coerce").fillna(0) > 0).astype("int8")
analysis["rebuild_scope"] = "Firm-level treatment/control and PSM covariates; patent-year outcomes unavailable"
analysis = analysis[[
    "full_firm_id", "organization_name", "founding_year", "vd_backed",
    "first_vd_year", "g_first_vd", "first_vc_year", "time_first_vc",
    "funding_rounds_ref", "ln_funding_ref", "industry2", "region2",
    "prior_patent", "rebuild_scope"
]]
primary = ROOT / "outputs/csdid_ultimately_granted_primary"
primary.mkdir(parents=True, exist_ok=True)
analysis.to_stata(primary / "csdid_ultimately_granted_full7316_controls.dta", write_index=False, version=118)
analysis.to_csv(primary / "csdid_ultimately_granted_full7316_controls.csv", index=False, encoding="utf-8-sig")

summary = pd.DataFrame([
    ["merged_v4 raw VD-backed firms", int(audit.vd_backed_v4_raw.sum())],
    ["merged_v4 after Dermira/Eargo correction", int(audit.vd_backed_v4_corrected.sum())],
    ["legacy 240626 raw VD-backed firms", int(audit.vd_backed_legacy_raw.fillna(0).sum())],
    ["legacy 240626 after Dermira/Eargo correction", int(audit.vd_backed_legacy_corrected.fillna(0).sum())],
    ["treatment-definition disagreements", int(audit.treatment_definition_disagrees.sum())],
    ["firms without legacy normalized-name match", int(audit.vd_backed_legacy_corrected.isna().sum())],
], columns=["metric", "value"])
summary.to_stata(OUT / "treatment_count_summary.dta", write_index=False, version=118)
summary.to_csv(OUT / "treatment_count_summary.csv", index=False, encoding="utf-8-sig")

# Firm-level bridge explaining 1,442 raw VD firms -> 1,440 corrected VD firms
# -> 1,410 complete treated firms used by the historical-reference PSM.
bridge = legacy.loc[legacy.vd_backed_legacy_raw.eq(1)].copy()
bridge["user_recode_non_vd"] = bridge["OrganizationName"].isin(["Dermira", "Eargo"]).astype("int8")
bridge["missing_reference_funding"] = bridge["ln_Total_Funding_Amount_FirstVD"].isna().astype("int8")
bridge["psm_treated_eligible"] = (
    bridge.vd_backed_legacy_corrected.eq(1)
    & bridge[["Founding_Year", "Industry2", "NumberOfFunding_Rounds_FirstVD",
              "ln_Total_Funding_Amount_FirstVD", "Region2", "TimeToFirst_VC"]].notna().all(axis=1)
).astype("int8")
bridge["bridge_status"] = "Included among 1,410 PSM-treated firms"
bridge.loc[bridge.user_recode_non_vd.eq(1), "bridge_status"] = "Excluded: user-verified non-VD"
bridge.loc[(bridge.user_recode_non_vd.eq(0)) & bridge.missing_reference_funding.eq(1), "bridge_status"] = (
    "Excluded: missing log funding at VD reference year"
)
bridge = bridge.rename(columns={"OrganizationName": "organization_name"})[[
    "organization_name", "Founding_Year", "vd_backed_legacy_raw",
    "vd_backed_legacy_corrected", "VD_Year",
    "NumberOfFunding_Rounds_FirstVD", "ln_Total_Funding_Amount_FirstVD",
    "user_recode_non_vd", "missing_reference_funding",
    "psm_treated_eligible", "bridge_status"
]]
for string_col in ["organization_name", "bridge_status"]:
    bridge[string_col] = bridge[string_col].fillna("").astype(str)
assert len(bridge) == 1442
assert bridge.vd_backed_legacy_corrected.sum() == 1440
assert bridge.psm_treated_eligible.sum() == 1410
bridge.to_stata(OUT / "vd_1442_to_1410_firm_audit.dta", write_index=False, version=118)
bridge.to_csv(OUT / "vd_1442_to_1410_firm_audit.csv", index=False, encoding="utf-8-sig")

print(summary.to_string(index=False))
print("\nDisagreements:")
print(audit.loc[audit.treatment_definition_disagrees.eq(1), cols[:1] + ["organization_name", "vd_backed_v4_corrected", "vd_backed_legacy_corrected", "treatment_note"]].to_string(index=False))
