from pathlib import Path
from collections import defaultdict
import csv, io, re, zipfile
import numpy as np
import pandas as pd

ROOT=Path(r"C:\Users\user\Documents\VD")
SRC=ROOT/"outputs/patentsview_2024_full_cohort/source"
OUT=ROOT/"outputs/csdid_historical_replication"
OUT.mkdir(parents=True,exist_ok=True)
ROSTER=ROOT/"outputs/csdid_ultimately_granted_primary/csdid_ultimately_granted_full7316_controls.dta"
BASEPANEL=ROOT/"outputs/csdid_replicated_from_rebuilt_patent_list/csdid_rebuilt_patent_panel.dta"
SUFFIXES={"inc","incorporated","corp","corporation","co","company","llc","ltd","limited","lp","llp","plc","holdings","holding"}

def norm(v):
    words=re.findall(r"[a-z0-9]+",str(v or "").casefold().replace("&"," and "))
    while words and words[-1] in SUFFIXES: words.pop()
    return " ".join(words)

def rows(path):
    with zipfile.ZipFile(path) as z:
        with z.open(z.namelist()[0]) as b:
            yield from csv.DictReader(io.TextIOWrapper(b,encoding="utf-8-sig",errors="replace"),delimiter="\t")

roster=pd.read_stata(ROSTER,convert_categoricals=False)[["full_firm_id","organization_name"]]
byname=defaultdict(list)
for r in roster.itertuples(index=False):
    k=norm(r.organization_name)
    if k: byname[k].append((int(r.full_firm_id),r.organization_name))

assoc={}
for r in rows(SRC/"g_assignee_disambiguated.tsv.zip"):
    k=norm(r.get("disambig_assignee_organization",""))
    if k not in byname: continue
    pid=str(r.get("patent_id","")).strip()
    if not pid: continue
    for fid,name in byname[k]:
        key=(fid,pid)
        x=assoc.setdefault(key,{"full_firm_id":fid,"organization_name":name,"patent_id":pid,
                                "matched_assignee_labels":set(),"assignee_ids":set()})
        x["matched_assignee_labels"].add(str(r.get("disambig_assignee_organization","")))
        if r.get("assignee_id"): x["assignee_ids"].add(str(r["assignee_id"]))
print("linked firm-patent pairs after disambiguated source",len(assoc),flush=True)

# The historical build also used raw assignee labels. The much smaller PGPub raw
# assignee table plus the official PGPub-to-grant crosswalk recovers those links
# without materializing the deleted grant raw-assignee archive.
raw_pg={}; pg_lookup=defaultdict(list)
for r in rows(SRC/"pg_assignee_not_disambiguated.tsv.zip"):
    k=norm(r.get("raw_assignee_organization",""))
    if k not in byname: continue
    pg=str(r.get("pgpub_id","")).strip()
    if not pg: continue
    for fid,name in byname[k]:
        x=raw_pg.setdefault((fid,pg),{"name":name,"labels":set(),"ids":set()})
        if fid not in pg_lookup[pg]: pg_lookup[pg].append(fid)
        x["labels"].add(str(r.get("raw_assignee_organization","")))
        if r.get("assignee_id"): x["ids"].add(str(r["assignee_id"]))
for r in rows(SRC/"pg_granted_pgpubs_crosswalk.tsv.zip"):
    pg=str(r.get("pgpub_id","")).strip(); pid=str(r.get("patent_id","")).strip()
    if not pg or not pid: continue
    for fid in pg_lookup.get(pg,[]):
        x=raw_pg[(fid,pg)]
        key=(fid,pid)
        a=assoc.setdefault(key,{"full_firm_id":fid,"organization_name":x["name"],"patent_id":pid,
                                "matched_assignee_labels":set(),"assignee_ids":set()})
        a["matched_assignee_labels"].update(x["labels"]); a["assignee_ids"].update(x["ids"])
print("linked firm-patent pairs after raw PGPub crosswalk union",len(assoc),flush=True)

# Exact historical second source: raw assignee labels attached to granted patents.
for r in rows(SRC/"g_assignee_not_disambiguated.tsv.zip"):
    k=norm(r.get("raw_assignee_organization",""))
    if k not in byname: continue
    pid=str(r.get("patent_id","")).strip()
    if not pid: continue
    for fid,name in byname[k]:
        key=(fid,pid)
        a=assoc.setdefault(key,{"full_firm_id":fid,"organization_name":name,"patent_id":pid,
                                "matched_assignee_labels":set(),"assignee_ids":set()})
        a["matched_assignee_labels"].add(str(r.get("raw_assignee_organization","")))
        if r.get("assignee_id"): a["assignee_ids"].add(str(r["assignee_id"]))
print("linked firm-patent pairs after exact historical raw grant union",len(assoc),flush=True)

wanted={pid for _,pid in assoc}
pinfo={}
for r in rows(SRC/"g_patent.tsv.zip"):
    pid=str(r.get("patent_id","")).strip()
    if pid in wanted:
        pinfo[pid]=(r.get("patent_type",""),r.get("patent_date",""),r.get("patent_title",""),r.get("withdrawn",""))
filing={}; appid={}
for r in rows(SRC/"g_application.tsv.zip"):
    pid=str(r.get("patent_id","")).strip()
    if pid in wanted:
        dt=str(r.get("filing_date","")).strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}",dt):
            filing.setdefault(pid,dt); appid.setdefault(pid,str(r.get("application_id","")).strip())

out=[]
for (fid,pid),x in assoc.items():
    typ,gdate,title,withdrawn=pinfo.get(pid,("","","",""))
    fdate=filing.get(pid,"")
    if typ!="utility" or withdrawn not in {"0",""} or not fdate: continue
    out.append({"full_firm_id":fid,"organization_name":x["organization_name"],"patent_id":pid,
                "application_id":appid.get(pid,"UNMAPPED_GRANT_"+pid),"filing_date":fdate,
                "filing_year":int(fdate[:4]),"grant_date":gdate,
                "grant_year":int(gdate[:4]) if re.match(r"\d{4}",gdate) else np.nan,
                "patent_title":title,"link_source":"exact_normalized_name_disambiguated",
                "matched_assignee_label":"|".join(sorted(x["matched_assignee_labels"])),
                "assignee_id":"|".join(sorted(x["assignee_ids"]))})
legacy=pd.DataFrame(out).drop_duplicates(["full_firm_id","application_id"])
legacy.to_csv(OUT/"legacy_grant_application_linkage_rebuilt.csv",index=False,encoding="utf-8-sig")

cnt=(legacy[legacy.filing_year.le(2024)].groupby(["full_firm_id","filing_year"]).application_id.nunique()
     .rename("apps_ult_granted").reset_index().rename(columns={"filing_year":"year"}))
panel=pd.read_stata(BASEPANEL,convert_categoricals=False)
panel=panel.drop(columns=[c for c in ["apps_ult_granted","ln1p_apps_ult_granted","cum_apps","prior_apps_l1","prior_patent_l1","prior_apps_G","prior_patent_G"] if c in panel])
panel=panel.merge(cnt,on=["full_firm_id","year"],how="left",validate="one_to_one")
panel["apps_ult_granted"]=panel.apps_ult_granted.fillna(0).astype(float)
panel["ln1p_apps_ult_granted"]=np.log1p(panel.apps_ult_granted)
panel=panel.sort_values(["full_firm_id","year"])
panel["cum_apps"]=panel.groupby("full_firm_id").apps_ult_granted.cumsum()
panel["prior_apps_l1"]=panel.groupby("full_firm_id").cum_apps.shift(1).fillna(0)
panel["prior_patent_l1"]=(panel.prior_apps_l1>0).astype(int)
panel["prior_granted_dummy_l1"]=panel["prior_patent_l1"]
panel["early_stage_main_l1"]=panel.groupby("full_firm_id").early_stage.shift(1)
panel["early_stage_main_l1"]=panel.early_stage_main_l1.fillna(1)
atg=panel[(panel.g_first_vd>0)&(panel.year==panel.g_first_vd)][["full_firm_id","prior_apps_l1","prior_patent_l1"]].rename(columns={"prior_apps_l1":"prior_apps_G","prior_patent_l1":"prior_patent_G"})
panel=panel.merge(atg,on="full_firm_id",how="left")
for c in panel.select_dtypes(include=["object","string"]).columns: panel[c]=panel[c].fillna("").astype(str)
panel.to_stata(OUT/"MASTER_CS_TABLE_rebuilt.dta",write_index=False,version=118)
pd.DataFrame({"metric":["legacy_rows","legacy_unique_applications","linked_firms","panel_rows","panel_firms"],
              "value":[len(legacy),legacy.application_id.nunique(),legacy.full_firm_id.nunique(),len(panel),panel.full_firm_id.nunique()]}).to_csv(OUT/"rebuild_QA.csv",index=False)
print(pd.read_csv(OUT/"rebuild_QA.csv").to_string(index=False),flush=True)
