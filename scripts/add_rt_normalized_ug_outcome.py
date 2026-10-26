"""Add right-truncation-normalized ultimately-granted patent counts.

The empirical grant-lag distribution is estimated from mature filing cohorts
(2010-2014).  For a filing year y, follow-up is 2024-y years.  Each grant
observed by 2024 receives inverse-completion weight 1/F(2024-y), where F(k)
is the fraction of eventual grants in the mature cohorts granted within k
years of filing.  The resulting firm-year sum estimates the number of those
applications that will ultimately be granted after registration is complete.

Both the uncapped estimate and a weight-capped-at-10 robustness version are
saved.  Existing columns are preserved.
"""

from pathlib import Path
import shutil
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\user\Documents\VD")
SRC = ROOT / "outputs" / "csdid_union_corrected_3yr" / "application_level_union_corrected_visible_mismatches.csv"
OUT = ROOT / "outputs" / "csdid_all_applications_corrected"
PANEL_DTA = OUT / "firm_year_all_applications_and_truncation_specs.dta"
PANEL_CSV = OUT / "firm_year_all_applications_and_truncation_specs.csv"
BACKUP_DTA = OUT / "firm_year_all_applications_and_truncation_specs_before_rt_normalization.dta"
QA_FILE = OUT / "ug_right_truncation_normalization_QA.csv"

apps = pd.read_csv(SRC, low_memory=False)
for v in ["filing_year", "ultimately_granted", "grant_lag_years"]:
    apps[v] = pd.to_numeric(apps[v], errors="coerce")
apps["ultimately_granted"] = apps["ultimately_granted"].fillna(0)
apps = apps.loc[apps["filing_year"].between(2010, 2024)].drop_duplicates(
    ["full_firm_id", "application_id"]
).copy()

# Mature cohorts have at least ten years of potential follow-up by 2024.
mature_grants = apps.loc[
    apps["ultimately_granted"].eq(1)
    & apps["filing_year"].between(2010, 2014)
    & apps["grant_lag_years"].notna()
].copy()
if mature_grants.empty:
    raise RuntimeError("No mature granted applications available to estimate the lag CDF.")

max_age = 2024 - 2010
cdf = {
    age: float((mature_grants["grant_lag_years"] <= age).mean())
    for age in range(max_age + 1)
}

apps["grant_followup_years"] = (2024 - apps["filing_year"]).clip(lower=0, upper=max_age).astype(int)
apps["ug_completion_rate"] = apps["grant_followup_years"].map(cdf)
if (apps["ug_completion_rate"] <= 0).any():
    bad = sorted(apps.loc[apps["ug_completion_rate"] <= 0, "grant_followup_years"].unique())
    raise RuntimeError(f"Zero completion probability for follow-up ages: {bad}")

apps["ug_rt_lag_weight"] = 1.0 / apps["ug_completion_rate"]
apps["ug_rt_lag_weight_cap10"] = apps["ug_rt_lag_weight"].clip(upper=10.0)
apps["ug_rt_lag_ipw"] = apps["ultimately_granted"] * apps["ug_rt_lag_weight"]
apps["ug_rt_lag_ipw_cap10"] = apps["ultimately_granted"] * apps["ug_rt_lag_weight_cap10"]

# Main normalization: remove the filing-year-specific observed grant rate.
# This is bounded by the observed application universe and does not extrapolate
# the very incomplete 2024 publication cohort by a factor of 62.
year_grant_rate = apps.groupby("filing_year")["ultimately_granted"].mean()
apps["ug_rt_year_grant_rate"] = apps["filing_year"].map(year_grant_rate)
apps["ug_rt_year_weight"] = 1.0 / apps["ug_rt_year_grant_rate"]
apps["grantedapp_norm"] = apps["ultimately_granted"] * apps["ug_rt_year_weight"]

annual = (
    apps.groupby(["full_firm_id", "filing_year"], as_index=False)
    .agg(
        grantedapp_norm=("grantedapp_norm", "sum"),
        ug_rt_lag_ipw=("ug_rt_lag_ipw", "sum"),
        ug_rt_lag_ipw_cap10=("ug_rt_lag_ipw_cap10", "sum"),
        ug_rt_year_grant_rate=("ug_rt_year_grant_rate", "first"),
        ug_rt_year_weight=("ug_rt_year_weight", "first"),
        ug_rt_completion_rate=("ug_completion_rate", "first"),
        ug_rt_lag_inverse_weight=("ug_rt_lag_weight", "first"),
    )
    .rename(columns={"filing_year": "year"})
)

panel_source = BACKUP_DTA if BACKUP_DTA.exists() else PANEL_DTA
panel = pd.read_stata(panel_source, convert_categoricals=False)
drop_existing = [c for c in annual.columns if c not in ["full_firm_id", "year"] and c in panel.columns]
if drop_existing:
    panel = panel.drop(columns=drop_existing)
panel = panel.merge(annual, on=["full_firm_id", "year"], how="left", validate="one_to_one")

# No observed application/grant in an otherwise observed firm-year is a true zero.
for v in ["grantedapp_norm", "ug_rt_lag_ipw", "ug_rt_lag_ipw_cap10"]:
    panel[v] = panel[v].fillna(0.0)

# The filing-year completion rate and inverse weight are common to every firm.
year_rates = annual[["year", "ug_rt_year_grant_rate", "ug_rt_year_weight",
                     "ug_rt_completion_rate", "ug_rt_lag_inverse_weight"]].drop_duplicates("year")
panel = panel.drop(columns=[c for c in year_rates.columns if c != "year" and c in panel.columns])
panel = panel.merge(year_rates, on="year", how="left", validate="many_to_one")

if not BACKUP_DTA.exists():
    shutil.copy2(PANEL_DTA, BACKUP_DTA)
panel.to_stata(PANEL_DTA, write_index=False, version=118)
panel.to_csv(PANEL_CSV, index=False)

qa = pd.DataFrame({
    "filing_year": list(range(2010, 2025)),
})
qa["followup_years"] = 2024 - qa["filing_year"]
qa["completion_rate"] = qa["followup_years"].map(cdf)
qa["inverse_weight"] = 1.0 / qa["completion_rate"]
qa["inverse_weight_cap10"] = qa["inverse_weight"].clip(upper=10.0)
observed = apps.groupby("filing_year").agg(
    observed_applications=("application_id", "size"),
    observed_grants=("ultimately_granted", "sum"),
    observed_grant_rate=("ug_rt_year_grant_rate", "first"),
    filing_year_normalized_grants=("grantedapp_norm", "sum"),
    lag_ipw_grants=("ug_rt_lag_ipw", "sum"),
    lag_ipw_grants_cap10=("ug_rt_lag_ipw_cap10", "sum"),
).reset_index()
qa = qa.merge(observed, on="filing_year", how="left")
qa.to_csv(QA_FILE, index=False)

print(f"Mature grants used for lag CDF: {len(mature_grants):,}")
print(qa.to_string(index=False))
print(f"Updated: {PANEL_DTA}")
print(f"Backup:  {BACKUP_DTA}")
