from pathlib import Path
import sys, json, zipfile, re
import pandas as pd
import numpy as np
from build_forward_citation_year_panel import explode_grants

R=Path(r'C:\Users\user\Documents\VD')
O=R/'outputs/table4_window3_39249_20261019'
O.mkdir(exist_ok=True,parents=True)
P=R/'outputs/patentsview_2024_full_cohort/source'
def chunks(path,cols):
    with zipfile.ZipFile(path) as z:
        with z.open(next(n for n in z.namelist() if not n.endswith('/'))) as f:
            yield from pd.read_csv(f,sep='\t',usecols=cols,dtype='string',chunksize=1000000)
def key(s): return re.sub('[^a-z0-9]','',str(s).lower())

a=pd.read_csv(R/'outputs/csdid_union_corrected_3yr/application_level_union_corrected_visible_mismatches.csv',dtype={'application_id':'string'},low_memory=False)
a=a[a.filing_year.between(2010,2024)].drop_duplicates(['full_firm_id','application_id']).copy()
assert len(a)==39249
assert not a.application_id.duplicated().any(), 'Multiple owners require owner-preserving joins'
g=explode_grants(a[a.ultimately_granted.eq(1)]).drop_duplicates(['application_id','patent_id'])
targets=set(g.patent_id.astype(str))
cache=O/'citation_edges.csv'
if cache.exists():
    e=pd.read_csv(cache,dtype='string')
else:
    parts=[]
    for i,c in enumerate(chunks(P/'g_us_patent_citation.tsv.zip',['patent_id','citation_patent_id'])):
        x=c[c.citation_patent_id.isin(targets)]
        if len(x): parts.append(x)
        if i%10==0: print('Citation scan chunks',i,flush=True)
    e=pd.concat(parts).drop_duplicates().rename(columns={'patent_id':'citing_patent_id','citation_patent_id':'patent_id'})
    e.to_csv(cache,index=False)
print('Edges',len(e),flush=True)
ids=set(e.citing_patent_id)|targets
dates=[]
for c in chunks(P/'g_patent.tsv.zip',['patent_id','patent_date']):
    dates.append(c[c.patent_id.isin(ids)])
d=pd.concat(dates).drop_duplicates('patent_id')
d['patent_date']=pd.to_datetime(d.patent_date,errors='coerce')
g['patent_id']=g.patent_id.astype(str)
g=g.drop(columns='grant_date').merge(d.rename(columns={'patent_date':'grant_date'}),on='patent_id',how='left',validate='many_to_one')
assert g.grant_date.notna().all()
e=e.merge(d.rename(columns={'patent_id':'citing_patent_id','patent_date':'citing_date'}),on='citing_patent_id',how='left',validate='many_to_one')
missing=int(e.citing_date.isna().sum())
e=e.merge(g,on='patent_id',how='inner',validate='many_to_one')
before=int(e.citing_date.lt(e.grant_date).sum())
e=e[e.citing_date.ge(e.grant_date)&e.citing_date.lt('2025-01-01')].copy()
e['year']=e.citing_date.dt.year
e=e.drop_duplicates(['application_id','citing_patent_id'])
e.to_csv(O/'dated_citation_edges_corrected.csv',index=False)
c=e.groupby(['application_id','year']).size().rename('n_cites').reset_index()
meta=g.groupby('application_id',as_index=False).agg(full_firm_id=('full_firm_id','first'),filing_year=('filing_year','first'))
cpc=pd.read_csv(R/'outputs/table2_forward_citation_year_methods_39249/application_citation_year_grid.csv',usecols=['application_id','cpc3'],dtype={'application_id':'string'}).drop_duplicates('application_id')
meta=meta.merge(cpc,on='application_id',validate='one_to_one')
grid=meta.merge(pd.DataFrame({'year':range(2010,2025)}),how='cross')
grid=grid[grid.year.ge(grid.filing_year)].merge(c,on=['application_id','year'],how='left',validate='one_to_one')
grid.n_cites=grid.n_cites.fillna(0)
for col,groups in [('fwd_norm_cohort',['filing_year','year']),('fwd_norm_cohort_cpc',['filing_year','year','cpc3'])]:
    mean=grid.groupby(groups).n_cites.transform('mean')
    assert mean.notna().all()
    grid[col]=np.divide(grid.n_cites,mean,out=np.zeros(len(grid)),where=mean.gt(0))
grid.to_csv(O/'application_year_corrected.csv',index=False)
outcomes=['fwd_norm_cohort','fwd_norm_cohort_cpc']
tot=grid.groupby('application_id',as_index=False)[outcomes].sum()
a=a.merge(tot,on='application_id',how='left',validate='one_to_one')
a['name_key']=a.organization_name.map(key)
m=pd.read_stata(R/'outputs/psm_final_2820_package/table3_current_2820_cross_section_v2.dta',convert_categoricals=False)
m=m[['firm_id','OrganizationName','VD','VDyear','Foundingyear','Region2','Industry2','priorpatentdummy_VD','earlystage','ln_MoneyRaised_VD','NumofFundingRounds_VD']].copy()
m['name_key']=m.OrganizationName.map(key)
assert not m.name_key.duplicated().any()
w=a.merge(m[['firm_id','name_key','VDyear']],on='name_key',how='inner',validate='many_to_one')
w=w[w.filing_year.sub(w.VDyear).between(1,3)&w.ultimately_granted.eq(1)].copy()
assert w[outcomes].notna().all().all()
w.to_csv(O/'eligible_postvd_applications.csv',index=False)
s=w.groupby('firm_id').agg(n_granted_win3=('application_id','nunique'),fwd_norm_cohort=('fwd_norm_cohort','sum'),fwd_norm_cohort_cpc=('fwd_norm_cohort_cpc','sum')).reset_index()
m=m.merge(s,on='firm_id',how='left',validate='one_to_one')
m[['n_granted_win3']+outcomes]=m[['n_granted_win3']+outcomes].fillna(0)
for col,short in zip(outcomes,['cohort','cpc']):
    m['quality_'+short]=np.divide(m[col],m.n_granted_win3,out=np.zeros(len(m)),where=m.n_granted_win3.gt(0))
    m['ln_quality_'+short]=np.log1p(m['quality_'+short])
m['complete_win3']=m.VDyear.le(2021).astype(int)
m['VD_prior']=m.VD*m.priorpatentdummy_VD
m['VD_early']=m.VD*m.earlystage
m.to_csv(O/'firm_crosssection_window3.csv',index=False)
m.to_stata(O/'firm_crosssection_window3.dta',write_index=False,version=118)
qa={'applications':len(a),'grant_linked_applications':len(meta),'valid_application_citing_edges':len(e),'missing_citing_dates':missing,'pre_grant_edges_excluded':before,'matched_firms':len(m),'complete_window_firms':int(m.complete_win3.sum()),'incomplete_window_firms':int((1-m.complete_win3).sum()),'firms_with_eligible_patents':int(m.n_granted_win3.gt(0).sum()),'eligible_postvd_applications':len(w),'date_source':'g_patent.patent_date of citing patent, NOT g_us_patent_citation.citation_date','year_FE':'Foundingyear, matching existing Table 4 specification','window':'filing_year - VDyear in [1,3]; citations observed through 2024','no_patent_convention':'quality=0 when denominator=0, explicitly following full-firm table convention'}
(O/'QA.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
print(json.dumps(qa,indent=2),flush=True)
