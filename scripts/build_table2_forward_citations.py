from pathlib import Path
import json
import math
import shutil
import sys

import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\user\Documents\VD")
OUT = ROOT / "outputs" / "table2_forward_citations_application_level"
OUT.mkdir(parents=True, exist_ok=True)

APPS = ROOT / "outputs" / "patent_application_list_rebuilt_2024" / "patent_application_list_through_2024.csv"
OLD = ROOT / "outputs" / "claude_replication_reference" / "data" / "application_level_list_through2024_used.csv"
PANEL = ROOT / "outputs" / "csdid_replicated_from_rebuilt_patent_list" / "csdid_rebuilt_patent_panel.csv"

apps = pd.read_csv(APPS, dtype={"application_id": str}, low_memory=False)
old = pd.read_csv(OLD, dtype={"application_id": str}, low_memory=False)
old_cites = old[["application_id", "forward_citations_through_2024"]].drop_duplicates("application_id")
apps = apps.merge(old_cites, on="application_id", how="left", validate="one_to_one")
apps["citation_eligible"] = apps["ultimately_granted"].eq(1)
apps["citation_observed_in_recovered_snapshot"] = apps["forward_citations_through_2024"].notna()

# PatentsView citation tables contain rows for actual citing-cited links. After
# joining the link counts to the granted-patent universe, absence is a zero.
apps["forward_citations_raw"] = np.where(
    apps["citation_eligible"], apps["forward_citations_through_2024"].fillna(0), np.nan
)

# Huang, Shu and Tian (2025) divide citations by the mean for the same filing
# year and three-digit technology class. Per the project decision, technology
# classes/CPC are deliberately omitted; the denominator is the filing-year
# mean among the linked granted applications in this cohort.
den = (
    apps.loc[apps.citation_eligible]
    .groupby("filing_year", as_index=False)["forward_citations_raw"]
    .agg(["mean", "count"])
    .reset_index()
    .rename(columns={"mean": "filing_year_mean_raw_citations", "count": "filing_year_granted_applications"})
)
apps = apps.merge(den, on="filing_year", how="left")
apps["forward_citations_adjusted_year"] = np.where(
    apps.citation_eligible & apps.filing_year_mean_raw_citations.gt(0),
    apps.forward_citations_raw / apps.filing_year_mean_raw_citations,
    np.where(apps.citation_eligible, 0.0, np.nan),
)
apps["citation_method"] = np.where(
    apps.citation_eligible,
    "raw citations through 2024 divided by cohort filing-year mean; no CPC/technology-class split",
    "not eligible: no linked grant",
)
apps.to_csv(OUT / "application_level_forward_citations_through_2024.csv", index=False, encoding="utf-8-sig")
den.to_csv(OUT / "citation_normalization_by_filing_year.csv", index=False, encoding="utf-8-sig")

fy = (
    apps.loc[apps.citation_eligible]
    .groupby(["full_firm_id", "filing_year"], as_index=False)
    .agg(
        cited_granted_applications=("application_id", "nunique"),
        forward_citations_raw_mean=("forward_citations_raw", "mean"),
        forward_citations_raw_sum=("forward_citations_raw", "sum"),
        forward_citations_adjusted_mean=("forward_citations_adjusted_year", "mean"),
        forward_citations_adjusted_sum=("forward_citations_adjusted_year", "sum"),
    )
    .rename(columns={"filing_year": "year"})
)
panel = pd.read_csv(PANEL, low_memory=False)
panel = panel.merge(fy, on=["full_firm_id", "year"], how="left", validate="one_to_one")
for c in [
    "cited_granted_applications", "forward_citations_raw_mean", "forward_citations_raw_sum",
    "forward_citations_adjusted_mean", "forward_citations_adjusted_sum",
]:
    panel[c] = panel[c].fillna(0)
panel["G"] = panel.g_first_vd.fillna(0).astype(int)
panel["prior"] = panel.prior_patent_G.fillna(0).astype(int)
panel["early"] = panel.early_stage_G.fillna(0).astype(int)
panel = panel[(panel.year <= 2024) & ~((panel.G > 0) & (panel.G <= panel.founding_year))].copy()
panel.to_csv(OUT / "firm_year_panel_with_forward_citations.csv", index=False, encoding="utf-8-sig")

qa = {
    "applications": int(len(apps)),
    "granted_applications": int(apps.citation_eligible.sum()),
    "granted_with_recovered_citation_value": int((apps.citation_eligible & apps.citation_observed_in_recovered_snapshot).sum()),
    "granted_without_recovered_citation_row_treated_as_zero": int((apps.citation_eligible & ~apps.citation_observed_in_recovered_snapshot).sum()),
    "application_id_duplicates": int(apps.application_id.duplicated().sum()),
    "panel_rows": int(len(panel)),
    "panel_firms": int(panel.full_firm_id.nunique()),
    "normalization": "filing-year mean, no CPC/technology class",
    "citation_cutoff": 2024,
}
(OUT / "QA_summary.json").write_text(json.dumps(qa, indent=2), encoding="utf-8")

# Reuse the already validated Python implementation of the Callaway-Sant'Anna
# doubly robust estimator, but point it to this rebuilt panel.
src = ROOT / "outputs" / "claude_replication_reference" / "code" / "dripw.py"
text = src.read_text(encoding="utf-8").replace("P=pd.read_csv('hist_panel.csv',low_memory=False)", "P=pd.read_csv('firm_year_panel_with_forward_citations.csv',low_memory=False)")
text = text.replace("from scipy.optimize import minimize\n", "")
old_logit = '''def logit(X,d,w):
    def nll(b):
        z=X@b; return -(w*(d*z-np.logaddexp(0,z))).sum()+1e-6*(b@b)
    def gr(b):
        z=X@b; pr=1/(1+np.exp(-z)); return -X.T@(w*(d-pr))+2e-6*b
    b=minimize(nll,np.zeros(X.shape[1]),jac=gr,method='L-BFGS-B').x
    return 1/(1+np.exp(-(X@b)))'''
new_logit = '''def logit(X,d,w):
    b=np.zeros(X.shape[1])
    for _ in range(60):
        z=np.clip(X@b,-30,30); pr=1/(1+np.exp(-z))
        grad=X.T@(w*(d-pr))-2e-6*b
        v=w*pr*(1-pr)
        h=(X.T*v)@X+2e-6*np.eye(X.shape[1])
        try: step=np.linalg.solve(h,grad)
        except np.linalg.LinAlgError: step=np.linalg.lstsq(h,grad,rcond=None)[0]
        b=b+step
        if np.max(np.abs(step))<1e-8: break
    return 1/(1+np.exp(-(X@b)))'''
text = text.replace(old_logit, new_logit)
(OUT / "dripw_table2.py").write_text(text, encoding="utf-8")

print(json.dumps(qa, indent=2))
