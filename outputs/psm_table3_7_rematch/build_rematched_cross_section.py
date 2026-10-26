from pathlib import Path
import re
import numpy as np
import pandas as pd

ROOT=Path(r"C:\Users\user\Documents\VD")
OUT=ROOT/"outputs"/"psm_table3_7_rematch"
OUT.mkdir(parents=True,exist_ok=True)
V6=Path(r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms\exact matched sample v6 unmatched.xlsx")
LEGACY=Path(r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms\240626.dta")
OLD=Path(r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms\260122 winsorization.dta")
PANEL=ROOT/"outputs"/"table2_forward_citations_application_level"/"firm_year_panel_with_forward_citations.csv"
FULL=ROOT/"outputs"/"csdid_ultimately_granted_primary"/"csdid_ultimately_granted_full7316_controls.dta"

def key(x): return re.sub(r"[^a-z0-9]","",str(x).casefold())
def logit_score(X,y):
    xv=X.to_numpy(float); yv=y.to_numpy(float); b=np.zeros(xv.shape[1])
    for _ in range(400):
        eta=np.clip(xv@b,-30,30); p=1/(1+np.exp(-eta)); w=np.clip(p*(1-p),1e-9,None)
        z=eta+(yv-p)/w; sw=np.sqrt(w); bn=np.linalg.pinv(xv*sw[:,None])@(z*sw)
        if np.max(np.abs(bn-b))<1e-10: b=bn; break
        b=bn
    return 1/(1+np.exp(-np.clip(xv@b,-30,30)))

d=pd.read_excel(V6)
d["name_key"]=d["Organization Name"].map(key)
d["name_rank"]=d.groupby("name_key").cumcount()
l=pd.read_stata(LEGACY,convert_categoricals=False)
l["name_key"]=l.OrganizationName.map(key); l["name_rank"]=l.groupby("name_key").cumcount()
l=l[["name_key","name_rank","Patents_VD"]]
d=d.merge(l,on=["name_key","name_rank"],how="left")
d["Patents_VD"]=d.Patents_VD.fillna(d.Grant_VD)
d["ln_funding"]=np.log1p(pd.to_numeric(d.Total_Funding_Amount_FirstVD,errors="coerce"))
cats=pd.get_dummies(d[["Founding_Year","Region2","Industry2"]].astype(str),drop_first=True,dtype=float)
cont=d[["ln_funding","NumberOfFunding_Rounds_FirstVD","Patents_VD","TimeToFirst_VC"]].apply(pd.to_numeric,errors="coerce")
complete=pd.concat([cats,cont],axis=1).notna().all(axis=1)
e=d.loc[complete].copy(); X=pd.concat([cats.loc[complete],cont.loc[complete]],axis=1); X.insert(0,"const",1.)
e["pscore"]=logit_score(X,e.VD_Backing.astype(int))
t=e[e.VD_Backing.eq(1)].copy(); c=e[e.VD_Backing.eq(0)].copy()
lo=max(t.pscore.min(),c.pscore.min()); hi=min(t.pscore.max(),c.pscore.max())
t=t[t.pscore.between(lo,hi)].sort_values(["pscore","name_key","name_rank"])
c=c[c.pscore.between(lo,hi)].copy()
available=c.index.to_numpy(); cp=c.pscore.to_numpy(); pairs=[]
for pid,(ti,tr) in enumerate(t.iterrows(),1):
    j=int(np.argmin(np.abs(cp-tr.pscore))); ci=int(available[j])
    pairs.append((pid,ti,ci,float(abs(cp[j]-tr.pscore))))
    available=np.delete(available,j); cp=np.delete(cp,j)
assert len(pairs)==1410
ids=[i for x in pairs for i in (x[1],x[2])]
m=e.loc[ids].copy(); m["pair_id"]=np.nan; m["match_distance"]=np.nan
for pid,ti,ci,dist in pairs:
    m.loc[[ti,ci],"pair_id"]=pid; m.loc[[ti,ci],"match_distance"]=dist
# Prefer the exact Stata psmatch2 membership once that run is available.
stata_match=OUT/"psmatch2_no_caliper_matched.csv"
if stata_match.exists():
    sm=pd.read_csv(stata_match)
    sm=sm[["name_key","_pscore","_pdif"]].drop_duplicates("name_key")
    m=d.merge(sm,on="name_key",how="inner",validate="many_to_one")
    m["pscore"] = m["_pscore"]
    m["pair_id"] = np.nan
    m["match_distance"] = m["_pdif"]
    assert len(m)==2820 and int(m.VD_Backing.sum())==1410
m["reference_year"]=np.where(m.VD_Backing.eq(1),pd.to_numeric(m["VD Year"],errors="coerce"),m.Founding_Year+5)

p=pd.read_csv(PANEL)
fm=pd.read_stata(FULL,convert_categoricals=False)[["full_firm_id","organization_name"]].drop_duplicates("full_firm_id")
fm["name_key"]=fm.organization_name.map(key)
firm_map=fm.sort_values(["name_key","full_firm_id"])
firm_map["name_rank"]=firm_map.groupby("name_key").cumcount()
m=m.merge(firm_map[["full_firm_id","name_key","name_rank"]],on=["name_key","name_rank"],how="left",validate="one_to_one")
print("panel ID matches",int(m.full_firm_id.notna().sum()),"of",len(m))
print(m.loc[m.full_firm_id.isna(),["Organization Name","name_key","name_rank"]].head(50).to_string(index=False))
p=p.merge(m[["full_firm_id","reference_year"]],on="full_firm_id",how="inner")
p["rel_year"]=p.year-p.reference_year
w=p[p.rel_year.between(1,3)].copy()
agg=w.groupby("full_firm_id").agg(
    patent_apps_win3=("apps_ult_granted","sum"),
    citation_quality_win3=("forward_citations_adjusted_sum","sum"),
    followon_equity_win3=("annual_funding","sum"),
).reset_index()
for yr in [1,2,3]:
    a=p[p.rel_year.eq(yr)].groupby("full_firm_id")["annual_funding"].sum().rename(f"followon_equity_t{yr}")
    agg=agg.merge(a,on="full_firm_id",how="left")
ref=p[p.year.eq(p.reference_year)].sort_values("full_firm_id").drop_duplicates("full_firm_id")
ref=ref[["full_firm_id","early_stage","series_bplus"]]
m=m.merge(agg,on="full_firm_id",how="left").merge(ref,on="full_firm_id",how="left")
for c0 in ["patent_apps_win3","citation_quality_win3"]: m[c0]=m[c0].fillna(0)
m["early_stage"]=m.early_stage.fillna(1-m.series_bplus).fillna(0)
m["prior_patent"]=(m.Patents_VD>0).astype(int)
m["ln_patent_win3"]=np.log1p(m.patent_apps_win3)
m["ln_citation_quality_win3"]=np.log1p(m.citation_quality_win3.clip(lower=0))
m["ln_followon_equity_win3"]=np.log1p(m.followon_equity_win3)
for yr in [1,2,3]: m[f"ln_followon_equity_t{yr}"]=np.log1p(m[f"followon_equity_t{yr}"])

# Existing exit histories are available only for firms in the archived matched sample.
old=pd.read_stata(OLD,convert_categoricals=False)
old["name_key"]=old.OrganizationName.map(key); old["name_rank"]=old.groupby("name_key").cumcount()
exitcols=["name_key","name_rank","VDage3","acq3","public3","badexit3"]
m=m.merge(old[exitcols],on=["name_key","name_rank"],how="left")
m["exit_history_available"]=m.VDage3.notna().astype(int)

out=pd.DataFrame({
    "firm_id":m.full_firm_id,"OrganizationName":m["Organization Name"],"pair_id":m.pair_id,
    "name_key":m.name_key,
    "VD":m.VD_Backing.astype(int),"VDyear":m.reference_year,"Foundingyear":m.Founding_Year,
    "Industry2":pd.Categorical(m.Industry2).codes+1,"Region2":pd.Categorical(m.Region2).codes+1,
    "patentdummybyfiling":m.prior_patent,"earlystage":m.early_stage,
    "ln_MoneyRaised_VD":m.ln_funding,"NumofFundingRounds_VD":m.NumberOfFunding_Rounds_FirstVD,
    "ln_patentbyfiling_win3":m.ln_patent_win3,
    "ln_fwd_norm_cohort_win3":m.ln_citation_quality_win3,
    "ln_moneyraised_win3":m.ln_followon_equity_win3,
    "ln_moneyraised_win1":m.ln_followon_equity_t1,"ln_moneyraised_win2":m.ln_followon_equity_t2,
    "ln_moneyraised_y1":m.ln_followon_equity_t1,"ln_moneyraised_y2":m.ln_followon_equity_t2,"ln_moneyraised_y3":m.ln_followon_equity_t3,
    "moneyraised_win3_raw":m.followon_equity_win3,
    "VDage3":m.VDage3,"acq3":m.acq3,"public3":m.public3,"badexit3":m.badexit3,
    "exit_history_available":m.exit_history_available,"pscore":m.pscore,"match_distance":m.match_distance,
})
out.to_csv(OUT/"rematched_2820_cross_section.csv",index=False,encoding="utf-8-sig")
st=out.copy()
for c0 in st.select_dtypes(include="object"): st[c0]=st[c0].fillna("").astype(str)
st.to_stata(OUT/"rematched_2820_cross_section.dta",write_index=False,version=118)
pd.DataFrame([{"initial_firms":len(d),"eligible_firms":len(e),"matched_treated":int(out.VD.sum()),"matched_controls":int((out.VD==0).sum()),"matched_firms":len(out),"support_lower":lo,"support_upper":hi,"exit_histories_available":int(out.exit_history_available.sum())}]).to_csv(OUT/"build_summary.csv",index=False)

# Validate rebuilt outcomes against the archived cross-section wherever membership overlaps.
old2=old.copy(); old2["name_key"]=old2.OrganizationName.map(key)
chk=out.merge(old2,on="name_key",suffixes=("_new","_old"))
rows=[]
for a,b in [("ln_patentbyfiling_win3_new","ln_patentbyfiling_win3_old"),("ln_fwd_norm_cohort_win3_new","ln_fwd_norm_cohort_win3_old"),("ln_moneyraised_win3_new","ln_moneyraised_win3_old")]:
    z=chk[[a,b]].dropna(); rows.append({"new_variable":a,"old_variable":b,"N":len(z),"correlation":z.corr().iloc[0,1],"mean_new":z[a].mean(),"mean_old":z[b].mean()})
pd.DataFrame(rows).to_csv(OUT/"outcome_validation_against_archived.csv",index=False)

# Build the archived membership on the same rebuilt outcome definitions so coefficient
# differences isolate sample membership rather than mixing outcome vintages.
oa=old.copy(); oa["name_key"]=oa.OrganizationName.map(key); oa["name_rank"]=oa.groupby("name_key").cumcount()
oa=oa.merge(firm_map[["full_firm_id","name_key","name_rank"]],on=["name_key","name_rank"],how="left")
oa["reference_year"]=oa.VDyear
op=pd.read_csv(PANEL).merge(oa[["full_firm_id","reference_year"]],on="full_firm_id",how="inner")
op["rel_year"]=op.year-op.reference_year
ow=op[op.rel_year.between(1,3)]
oagg=ow.groupby("full_firm_id").agg(patent_apps_win3=("apps_ult_granted","sum"),citation_quality_win3=("forward_citations_adjusted_sum","sum"),followon_equity_win3=("annual_funding","sum")).reset_index()
for yr in [1,2,3]:
    aa=op[op.rel_year.eq(yr)].groupby("full_firm_id")["annual_funding"].sum().rename(f"followon_equity_t{yr}")
    oagg=oagg.merge(aa,on="full_firm_id",how="left")
oa=oa.merge(oagg,on="full_firm_id",how="left")
oldout=pd.DataFrame({
    "firm_id":oa.full_firm_id,"OrganizationName":oa.OrganizationName,"pair_id":np.nan,"name_key":oa.name_key,
    "VD":oa.VD,"VDyear":oa.VDyear,"Foundingyear":oa.Foundingyear,"Industry2":oa.Industry2,"Region2":oa.Region2,
    "patentdummybyfiling":oa.patentdummybyfiling,"earlystage":1-oa.SeriesB,
    "ln_MoneyRaised_VD":oa.ln_MoneyRaised_VD,"NumofFundingRounds_VD":oa.NumofFundingRounds_VD,
    "ln_patentbyfiling_win3":np.log1p(oa.patent_apps_win3.fillna(0)),
    "ln_fwd_norm_cohort_win3":np.log1p(oa.citation_quality_win3.fillna(0).clip(lower=0)),
    "ln_moneyraised_win3":np.log1p(oa.followon_equity_win3),
    "ln_moneyraised_win1":np.log1p(oa.followon_equity_t1),"ln_moneyraised_win2":np.log1p(oa.followon_equity_t2),
    "ln_moneyraised_y1":np.log1p(oa.followon_equity_t1),"ln_moneyraised_y2":np.log1p(oa.followon_equity_t2),"ln_moneyraised_y3":np.log1p(oa.followon_equity_t3),
    "moneyraised_win3_raw":oa.followon_equity_win3,
    "VDage3":oa.VDage3,"acq3":oa.acq3,"public3":oa.public3,"badexit3":oa.badexit3,
    "exit_history_available":1,"pscore":np.nan,"match_distance":np.nan,
})
out["sample_version"]="new_rematch"; oldout["sample_version"]="archived_membership"
both=pd.concat([oldout,out],ignore_index=True)
bs=both.copy()
for c0 in bs.select_dtypes(include="object"): bs[c0]=bs[c0].fillna("").astype(str)
bs.to_stata(OUT/"archived_and_rematched_cross_sections.dta",write_index=False,version=118)
both.to_csv(OUT/"archived_and_rematched_cross_sections.csv",index=False,encoding="utf-8-sig")
print(pd.read_csv(OUT/"build_summary.csv").to_string(index=False))
print(pd.read_csv(OUT/"outcome_validation_against_archived.csv").to_string(index=False))
