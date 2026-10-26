from pathlib import Path
import re
import json
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\user\Documents\VD")
OUT = ROOT / "outputs" / "csdid_replicated_from_rebuilt_patent_list"
OUT.mkdir(parents=True, exist_ok=True)
APPS = ROOT / "outputs" / "patent_application_list_rebuilt_2024" / "patent_application_list_through_2024.csv"
ROSTER = ROOT / "outputs" / "csdid_ultimately_granted_primary" / "csdid_ultimately_granted_full7316_controls.dta"
DEALS = Path(r"C:\Users\user\OneDrive\바탕 화면\2010 2015 Crunchbase deals merged_v4.xlsx")

def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).casefold())

roster = pd.read_stata(ROSTER, convert_categoricals=False)
roster["name_key"] = roster.organization_name.map(norm)
apps = pd.read_csv(APPS, low_memory=False)
apps["application_id"] = apps.application_id.astype(str)
apps["filing_year"] = pd.to_numeric(apps.filing_year, errors="coerce")
apps["ultimately_granted"] = pd.to_numeric(apps.ultimately_granted, errors="coerce").fillna(0).astype(int)
apps = apps.drop_duplicates(["full_firm_id", "application_id"])

deals = pd.read_excel(DEALS, header=1)
deals["name_key"] = deals["Organization Name"].map(norm)
deals["deal_year"] = pd.to_numeric(deals["Deal year"], errors="coerce")
deals["money_raised"] = pd.to_numeric(deals["Money Raised Currency (in USD)"], errors="coerce")
deals["stage_label"] = deals["Funding Stage"].fillna(deals["Funding Type"]).fillna("").astype(str)
deals["announced"] = pd.to_datetime(deals["Announced Date"], errors="coerce")
deals = deals.merge(roster[["full_firm_id", "name_key"]], on="name_key", how="inner")
deals = deals.sort_values(["full_firm_id", "deal_year", "announced", "deal no"])
annual = deals.groupby(["full_firm_id", "deal_year"], as_index=False).agg(
    annual_funding=("money_raised", "sum"),
    annual_rounds=("deal_year", "size"),
    latest_stage_year=("stage_label", lambda x: next((str(v) for v in reversed(x.tolist()) if str(v).strip()), "")),
)

rows=[]
for r in roster.itertuples(index=False):
    start=max(2010, int(r.founding_year))
    for year in range(start, 2025): rows.append((int(r.full_firm_id), year))
panel=pd.DataFrame(rows, columns=["full_firm_id","year"])
panel=panel.merge(roster.drop(columns="name_key"), on="full_firm_id", how="left", validate="many_to_one")
panel=panel.merge(annual, left_on=["full_firm_id","year"], right_on=["full_firm_id","deal_year"], how="left").drop(columns="deal_year")
panel["annual_funding"]=panel.annual_funding.fillna(0)
panel["annual_rounds"]=panel.annual_rounds.fillna(0)
panel["cum_funding"]=panel.groupby("full_firm_id").annual_funding.cumsum()
panel["cum_rounds"]=panel.groupby("full_firm_id").annual_rounds.cumsum()
panel["latest_stage"]=panel.groupby("full_firm_id").latest_stage_year.ffill().fillna("")
st=panel.latest_stage.str.casefold()
panel["early_stage"] = st.str.contains(r"pre-seed|seed|angel|early stage|series a", regex=True).astype(float)
panel.loc[panel.latest_stage.eq(""),"early_stage"]=np.nan
panel["series_bplus"] = st.str.contains(r"series b|series c|series d|series e|series f|series g|late stage|private equity|post-ipo", regex=True).astype(float)
panel.loc[panel.latest_stage.eq(""),"series_bplus"]=np.nan
panel["ln1p_cum_funding_l1"]=np.log1p(panel.groupby("full_firm_id").cum_funding.shift(1).fillna(0))
panel["cum_funding_rounds_l1"]=panel.groupby("full_firm_id").cum_rounds.shift(1).fillna(0)

g=(apps[apps.ultimately_granted.eq(1) & apps.filing_year.between(1900,2024)]
   .groupby(["full_firm_id","filing_year"]).application_id.nunique().rename("apps_ult_granted").reset_index())
g["filing_year"]=g.filing_year.astype(int)
panel=panel.merge(g,left_on=["full_firm_id","year"],right_on=["full_firm_id","filing_year"],how="left").drop(columns="filing_year")
panel["apps_ult_granted"]=panel.apps_ult_granted.fillna(0).astype(float)
panel["ln1p_apps_ult_granted"]=np.log1p(panel.apps_ult_granted)
panel=panel.sort_values(["full_firm_id","year"])
panel["cum_apps"]=panel.groupby("full_firm_id").apps_ult_granted.cumsum()
panel["prior_apps_l1"]=panel.groupby("full_firm_id").cum_apps.shift(1).fillna(0)
panel["prior_patent_l1"]=(panel.prior_apps_l1>0).astype(int)

atg=panel[(panel.g_first_vd>0)&(panel.year.eq(panel.g_first_vd))][["full_firm_id","prior_apps_l1","prior_patent_l1","early_stage","series_bplus","latest_stage"]].rename(columns={
    "prior_apps_l1":"prior_apps_G","prior_patent_l1":"prior_patent_G","early_stage":"early_stage_G","series_bplus":"series_bplus_G","latest_stage":"stage_G"})
panel=panel.merge(atg,on="full_firm_id",how="left")
panel["event_time"]=(panel.year-panel.g_first_vd).where(panel.g_first_vd>0)
panel["post_vd"]=((panel.g_first_vd>0)&(panel.year>=panel.g_first_vd)).astype(int)

# Preserve the historical categorical controls where available; missing values
# are explicit reference categories as in the earlier full-cohort panel build.
for c in ["time_first_vc","funding_rounds_ref","ln_funding_ref","industry2","region2"]:
    panel[c]=pd.to_numeric(panel[c],errors="coerce").fillna(0)
panel["industry_fe"]=panel.industry2.astype(int)
panel["region_fe"]=panel.region2.astype(int)

panel.to_csv(OUT/"csdid_rebuilt_patent_panel.csv",index=False,encoding="utf-8-sig")
dta=panel.copy()
for c in dta.select_dtypes(include=["object","string"]).columns: dta[c]=dta[c].fillna("").astype(str)
dta.to_stata(OUT/"csdid_rebuilt_patent_panel.dta",write_index=False,version=118)
qa={
    "applications":int(len(apps)),"ultimately_granted":int(apps.ultimately_granted.sum()),
    "panel_rows":int(len(panel)),"panel_firms":int(panel.full_firm_id.nunique()),
    "treated_firms":int(roster.g_first_vd.gt(0).sum()),
    "invalid_timing_firms":int(((roster.g_first_vd>0)&(roster.g_first_vd<=roster.founding_year)).sum()),
    "analysis_rows_after_timing_drop":int(len(panel[~((panel.g_first_vd>0)&(panel.g_first_vd<=panel.founding_year))])),
    "early_stage_treated":int(atg.early_stage_G.eq(1).sum()),"series_bplus_treated":int(atg.series_bplus_G.eq(1).sum()),
}
(OUT/"panel_QA.json").write_text(json.dumps(qa,indent=2),encoding="utf-8")
print(json.dumps(qa,indent=2))
