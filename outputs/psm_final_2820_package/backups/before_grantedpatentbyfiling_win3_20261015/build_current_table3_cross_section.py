from pathlib import Path
import re
import sys
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\user\Documents\VD")
PKG = ROOT / "outputs" / "psm_final_2820_package"
MATCHED = PKG / "psm_stata_matched_2820.dta"
FIRM_MAP = ROOT / "outputs" / "csdid_ultimately_granted_primary" / "csdid_ultimately_granted_full7316_controls.dta"
PANEL = ROOT / "outputs" / "table2_forward_citations_application_level" / "firm_year_panel_with_forward_citations.csv"
APPLICATIONS = ROOT / "outputs" / "csdid_union_corrected_3yr" / "application_level_union_corrected_visible_mismatches.csv"
CITATION_METHODS = ROOT / "outputs" / "table2_forward_citation_year_methods_39249" / "application_level_with_forward_citation_methods.csv"


def key(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


m = pd.read_stata(MATCHED, convert_categoricals=False)
m["name_key"] = m["OrganizationName"].map(key)

# Alternative outcome window requested for robustness: applications filed in
# years t+1 through t+3, excluding applications filed in the reference year t.
# This uses the same corrected 39,249 unique firm-application observations as
# patent_application_win3 (the latter retains its original t through t+3 window).
apps = pd.read_csv(APPLICATIONS, low_memory=False)
apps = apps.loc[apps["filing_year"].between(2010, 2024)].copy()
apps = apps.drop_duplicates(["full_firm_id", "application_id"])
assert len(apps) == 39249
apps["name_key"] = apps["organization_name"].map(key)
reference = m[["name_key", "Founding_Year", "VDYear"]].drop_duplicates().rename(
    columns={"Founding_Year": "founding_year", "VDYear": "reference_year"})
assert not reference["name_key"].duplicated().any()
apps = apps.merge(reference, on="name_key", how="inner", validate="many_to_one")
apps["application_id"] = apps["application_id"].astype(str)
methods = pd.read_csv(
    CITATION_METHODS,
    usecols=["full_firm_id", "application_id", "fwd_norm_total",
             "fwd_norm_cpc_total", "fwd_rate_norm_last"],
    dtype={"application_id": "string"}, low_memory=False)
methods["application_id"] = methods["application_id"].astype(str)
assert len(methods) == 39249
assert not methods[["full_firm_id", "application_id"]].duplicated().any()
apps = apps.merge(methods, on=["full_firm_id", "application_id"], how="left", validate="one_to_one")
assert apps[["fwd_norm_total", "fwd_norm_cpc_total", "fwd_rate_norm_last"]].notna().any(axis=1).sum() > 0
# Missing method values identify applications without a linked granted patent;
# these contribute zero forward citations but remain in the per-application denominator.
method_cols = ["fwd_norm_total", "fwd_norm_cpc_total", "fwd_rate_norm_last"]
apps[method_cols] = apps[method_cols].fillna(0.0)
apps["patentbyfiling_win3_2"] = apps["filing_year"].sub(apps["reference_year"]).between(1, 3).astype(int)
apps["priorpatent_VD_2"] = (
    apps["filing_year"].ge(apps["founding_year"])
    & apps["filing_year"].le(apps["reference_year"])
).astype(int)
application_counts = apps.groupby("name_key", as_index=False)[
    ["patentbyfiling_win3_2", "priorpatent_VD_2"]].sum()
# The matched Stata file now contains the corrected priorpatent_VD_2 used in
# matching. Recompute it here from the application file and replace the source
# column so this build remains independently auditable.
m = m.drop(columns=["priorpatent_VD_2"], errors="ignore")
m = m.merge(application_counts, on="name_key", how="left", validate="one_to_one")
m[["patentbyfiling_win3_2", "priorpatent_VD_2"]] = m[
    ["patentbyfiling_win3_2", "priorpatent_VD_2"]].fillna(0).astype(int)
assert m["patent_application_VD"].astype(int).eq(m["priorpatent_VD_2"]).all()

# Normalized forward citations per application for applications filed t+1..t+3.
# v1: filing-year cohort normalization; v2: filing-year x CPC3 normalization;
# v3: exposure-year annualized rate followed by filing-year normalization.
window_apps = apps.loc[apps["patentbyfiling_win3_2"].eq(1)].copy()
citation_counts = window_apps.groupby("name_key", as_index=False).agg(
    citation_window_apps=("application_id", "nunique"),
    citation_v1_sum=("fwd_norm_total", "sum"),
    citation_v2_sum=("fwd_norm_cpc_total", "sum"),
    citation_v3_sum=("fwd_rate_norm_last", "sum"),
)
assert (citation_counts["citation_window_apps"] > 0).all()
citation_counts["norm_cite_perpat_win3_v1"] = (
    citation_counts["citation_v1_sum"] / citation_counts["citation_window_apps"])
citation_counts["norm_cite_perpat_win3_v2"] = (
    citation_counts["citation_v2_sum"] / citation_counts["citation_window_apps"])
citation_counts["norm_cite_perpat_win3_v3"] = (
    citation_counts["citation_v3_sum"] / citation_counts["citation_window_apps"])
m = m.merge(citation_counts[["name_key", "citation_window_apps",
                             "norm_cite_perpat_win3_v1",
                             "norm_cite_perpat_win3_v2",
                             "norm_cite_perpat_win3_v3"]],
            on="name_key", how="left", validate="one_to_one")
m[["citation_window_apps", "norm_cite_perpat_win3_v1",
   "norm_cite_perpat_win3_v2", "norm_cite_perpat_win3_v3"]] = m[
    ["citation_window_apps", "norm_cite_perpat_win3_v1",
     "norm_cite_perpat_win3_v2", "norm_cite_perpat_win3_v3"]].fillna(0)
assert m["citation_window_apps"].astype(int).eq(m["patentbyfiling_win3_2"]).all()

# The panel and FIRM_MAP share one internal ID system.  Match that system to
# the PSM firms by normalized company name, never to the application union's
# unrelated full_firm_id numbering.
fm = pd.read_stata(FIRM_MAP, convert_categoricals=False)[["full_firm_id", "organization_name"]]
fm = fm.drop_duplicates("full_firm_id")
fm["name_key"] = fm["organization_name"].map(key)
fm = fm.sort_values(["name_key", "full_firm_id"]).drop_duplicates("name_key")
m = m.merge(fm[["name_key", "full_firm_id"]], on="name_key", how="left", validate="many_to_one")

p = pd.read_csv(PANEL, low_memory=False)
ref = m[["name_key", "full_firm_id", "VDYear"]].dropna(subset=["full_firm_id"])
q = p.merge(ref, on="full_firm_id", how="inner")
q = q.loc[q["year"].eq(q["VDYear"])].copy()
q["earlystage"] = q["early_stage"].fillna(1 - q["series_bplus"])
early = q.sort_values("name_key").drop_duplicates("name_key")[["name_key", "earlystage"]]
m = m.merge(early, on="name_key", how="left", validate="many_to_one")
# Preserve the convention used in the prior cross-sectional build: firms with
# no stage record at the reference year are coded as not early-stage.
m["earlystage"] = m["earlystage"].fillna(0)

out = pd.DataFrame({
    "firm_id": m["no"],
    "OrganizationName": m["OrganizationName"],
    "VD": m["VD_Backing"].astype(int),
    "VDyear": m["VDYear"],
    "Foundingyear": m["Founding_Year"],
    "Region2": m["Region2"],
    "Industry2": m["Industry2"],
    "patentdummybyfiling": m["patent_application_VD"].gt(0).astype(int),
    "earlystage": m["earlystage"],
    "ln_MoneyRaised_VD": m["ln_Total_Funding_Amount_FirstVD"],
    "NumofFundingRounds_VD": m["NumberOfFunding_Rounds_FirstVD"],
    "patent_application_win3": m["patent_application_win3"].astype(int),
    "patentbyfiling_win3_2": m["patentbyfiling_win3_2"].astype(int),
})
out["ln_patentbyfiling_win3"] = np.log1p(out["patent_application_win3"])
# Retain untransformed source values, not exponentiated approximations.
# NumofFundingRounds_VD and patent_application_win3 already contain raw counts.
out["MoneyRaised_VD"] = m["Total_Funding_Amount_FirstVD"]
out["patent_application_VD"] = m["patent_application_VD"].astype(int)
out["priorpatent_VD_2"] = m["priorpatent_VD_2"].astype(int)
out["priorpatentdummy_VD"] = out["priorpatent_VD_2"].gt(0).astype(int)
out["norm_cite_perpat_win3_v1"] = m["norm_cite_perpat_win3_v1"]
out["norm_cite_perpat_win3_v2"] = m["norm_cite_perpat_win3_v2"]
out["norm_cite_perpat_win3_v3"] = m["norm_cite_perpat_win3_v3"]
assert np.allclose(np.log1p(out["MoneyRaised_VD"]), out["ln_MoneyRaised_VD"], rtol=0, atol=1e-12)

assert len(out) == 2820 and out["VD"].sum() == 1410
assert int(out.loc[out.OrganizationName.eq("AliveCor"), "patent_application_win3"].iloc[0]) == 16
assert int(out.loc[out.OrganizationName.eq("Health Outcomes Sciences"), "patent_application_win3"].iloc[0]) == 0
assert out["patentbyfiling_win3_2"].le(out["patent_application_win3"]).all()

# Preserve source category codes and restore their original Stata value labels.
# CSV cannot store value labels, so explicit name columns accompany the codes.
source_categories = pd.read_stata(MATCHED)[["no", "Region2", "Industry2"]].set_index("no")
value_labels = {}
for variable in ["Region2", "Industry2"]:
    names = source_categories.loc[out["firm_id"], variable].astype(str).to_numpy()
    out[variable + "_label"] = names
    pairs = out[[variable, variable + "_label"]].drop_duplicates()
    assert pairs[variable].is_unique
    value_labels[variable] = dict(zip(pairs[variable].astype(int), pairs[variable + "_label"]))

# Audited corrections from the original merged_v4 Industry Classification.
# Only repair the legacy zero category; do not rematch or recode other firms.
corrections_path = PKG / "industry2_source_corrections.csv"
if corrections_path.exists():
    corrections = pd.read_csv(corrections_path).set_index("firm_id")
    assert corrections.index.is_unique
    codes = {label: code for code, label in value_labels["Industry2"].items()}
    for idx in out.index[out["Industry2_label"].eq("0")]:
        firm_id = out.at[idx, "firm_id"]
        if firm_id in corrections.index:
            fix = corrections.loc[firm_id]
            assert out.at[idx, "OrganizationName"] == fix["OrganizationName"]
            label = str(fix["Industry2_label"])
            out.at[idx, "Industry2"] = codes[label]
            out.at[idx, "Industry2_label"] = label

output_stem = sys.argv[1] if len(sys.argv) > 1 else "table3_current_2820_cross_section"
out.to_csv(PKG / (output_stem + ".csv"), index=False, encoding="utf-8-sig")
out.to_stata(PKG / (output_stem + ".dta"), write_index=False, version=118,
             value_labels=value_labels,
             variable_labels={"Region2": "Region category (source Region2)",
                              "Industry2": "Industry category (source Industry2)",
                              "patent_application_win3": "Applications filed in years t=0 to t+3",
                              "patentbyfiling_win3_2": "Applications filed in years t+1 to t+3",
                              "priorpatent_VD_2": "Applications filed from founding year through VD year",
                              "priorpatentdummy_VD": "One if at least one application from founding through VD year",
                              "norm_cite_perpat_win3_v1": "Normalized citations per patent t+1 to t+3: filing cohort",
                              "norm_cite_perpat_win3_v2": "Normalized citations per patent t+1 to t+3: filing cohort and CPC3",
                              "norm_cite_perpat_win3_v3": "Normalized citations per patent t+1 to t+3: exposure-adjusted rate"})
print(out[["patent_application_win3", "ln_patentbyfiling_win3", "earlystage"]].describe())
print("Missing earlystage:", int(out["earlystage"].isna().sum()))
