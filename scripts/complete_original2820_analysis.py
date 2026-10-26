"""Complete the original-sample schema without borrowing other firms' values.

Legacy controls are immutable. Reuse existing firm-level supplemental values
only for identical company AND reference year. Rebuild full-cohort quantities,
financing and statuses from sources. Uncollected innovation inputs stay missing
and are explicitly reported, never zero-filled.
"""
from pathlib import Path
import re, json, shutil, tempfile, subprocess
import numpy as np
import pandas as pd

ROOT=Path('C:/Users/user/Documents/VD')
PKG=ROOT/'outputs/psm_final_2820_package'
TARGET=PKG/'table3_original_2820_cross_section_v2.dta'
SOURCE=Path('C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms/260122 winsorization.dta')
BACK=PKG/'backups/before_full_original2820_20261020'
BACK.mkdir(parents=True,exist_ok=True)
for path in [TARGET,PKG/'RUN_TABLE3_PATENT_APPLICATION_WIN3_v2.do']:
    if not (BACK/path.name).exists(): shutil.copy2(path,BACK/path.name)
key=lambda x:re.sub('[^a-z0-9]','',str(x).casefold())
base=pd.read_stata(TARGET,convert_categoricals=False).set_index('firm_id')
legacy=pd.read_stata(SOURCE,convert_categoricals=False).set_index('firm_id')
current=pd.read_stata(PKG/'table3_current_2820_cross_section_v2.dta',convert_categoricals=False)
assert base.index.is_unique and len(base)==2820
controls=['VD','VDyear','Foundingyear','Region2','Industry2','patentdummybyfiling','earlystage','MoneyRaised_VD','ln_MoneyRaised_VD','NumofFundingRounds_VD']
pd.testing.assert_frame_equal(base[controls].sort_index(),legacy[controls].sort_index(),check_exact=True)
ref=base[['OrganizationName','VDyear','Foundingyear']].reset_index()
ref['name_key']=ref.OrganizationName.map(key)
assert ref.name_key.is_unique
current['name_key']=current.OrganizationName.map(key)
assert current.name_key.is_unique
cur=current.set_index(['name_key','VDyear'])
idx=pd.MultiIndex.from_frame(ref[['name_key','VDyear']])
same=cur.reindex(idx).set_axis(ref.firm_id)
extra=[c for c in current if c not in legacy and c not in ['firm_id','name_key','grantedpatentbyfiling_win3','grantedpatentbyfiling_norm_win3','norm_cite_perpat_win3_v4']]
out=same[extra].copy()
out['supplement_same_reference']=idx.isin(cur.index).astype('int8')
out['innovation_source_covered']=out.supplement_same_reference
for c in out.select_dtypes(include='object'): out[c]=out[c].fillna('')
provenance={c:'Existing supplemental data: exact company + reference-year match only' for c in extra}
apps=pd.read_csv(ROOT/'outputs/csdid_union_corrected_3yr/application_level_union_corrected_visible_mismatches.csv',dtype={'application_id':str},low_memory=False)
apps=apps[apps.filing_year.between(2010,2024)].copy()
assert len(apps)==39249 and not apps[['full_firm_id','application_id']].duplicated().any()
apps['name_key']=apps.organization_name.map(key)
apps=apps.merge(ref,on='name_key',how='inner',validate='many_to_one')
apps['event']=apps.filing_year-apps.VDyear
methods=pd.read_csv(ROOT/'outputs/table2_forward_citation_year_methods_39249/application_level_with_forward_citation_methods.csv',dtype={'application_id':str})
apps=apps.merge(methods[['full_firm_id','application_id','fwd_raw_total','fwd_norm_total','fwd_norm_cpc_total','fwd_rate_norm_last']],on=['full_firm_id','application_id'],how='left',validate='one_to_one')
win=apps[apps.event.between(1,3)].copy()
for name,frame in [('patentbyfiling_win3_2',win),('patent_application_win3',apps[apps.event.between(0,3)]),('priorpatent_VD_2',apps[apps.filing_year.between(apps.Foundingyear,apps.VDyear)])]:
    out[name]=frame.groupby('firm_id').size().reindex(out.index,fill_value=0)
    provenance[name]='Rebuilt on original reference year from complete 39249 application source'
out['patent_application_VD']=out.priorpatent_VD_2
# Do NOT substitute the updated patent count for the original moderator.
out['priorpatentdummy_VD']=legacy.patentdummybyfiling
for v,col in [(1,'fwd_norm_total'),(2,'fwd_norm_cpc_total'),(3,'fwd_rate_norm_last')]:
    out[f'norm_cite_perpat_win3_v{v}']=win.groupby('firm_id')[col].sum().reindex(out.index)/base.grantedpatentbyfiling_win3.replace(0,np.nan)
for v in (1,2,3,4):
    values=base.norm_cite_perpat_win3_v4 if v==4 else out[f'norm_cite_perpat_win3_v{v}']
    out[f'norm_cite_perpat_win3_vv{v}']=values.fillna(0)
out['applications_filed_win3']=out.patentbyfiling_win3_2
out['applications_granted_win3']=base.grantedpatentbyfiling_win3
out['grant_rate_win3']=out.applications_granted_win3/out.applications_filed_win3.replace(0,np.nan)
out['win3_observed']=base.win3_complete_2024

print('Reading original deal source...',flush=True)
dealpath=Path('C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms/2010 2015 Crunchbase deals merged_v4.xlsx')
deals=pd.read_excel(dealpath,header=1,usecols=['Organization Name','deal no','Deal year','Funding Type','Money Raised Currency (in USD)'])
deals['name_key']=deals['Organization Name'].map(key)
assert ref.name_key.isin(deals.name_key).all()
deals['amount']=pd.to_numeric(deals['Money Raised Currency (in USD)'],errors='coerce')
deals['year']=pd.to_numeric(deals['Deal year'],errors='coerce')
ft=deals['Funding Type'].fillna('').str.strip()
deals['equity']=ft.isin(['Seed','Pre-Seed','Angel','Venture - Series Unknown','Private Equity','Corporate Round','Equity Crowdfunding','Post-IPO Equity'])|ft.str.match(r'^Series [A-I](?:\d+)?$')
dw=deals.merge(ref[['firm_id','name_key','VDyear']],on='name_key',how='inner',validate='many_to_one')
dw['event']=dw.year-dw.VDyear
dw=dw[dw.event.between(1,3)]
assert not dw.duplicated(['firm_id','deal no']).any()
def amount_total(x):
    return x.sum(min_count=1) if x.notna().all() else np.nan
for prefix,rows in [('moneyraised',dw),('equityraised',dw[dw.equity])]:
    for t in (1,2,3):
        c=f'{prefix}_t{t}'
        out[c]=rows[rows.event.eq(t)].groupby('firm_id').amount.agg(amount_total).reindex(out.index)
        provenance[c]='Original deal source, original VDyear+t; no round/undisclosed = missing'
    c='Follow_on_Equity_Raised_win3' if prefix=='equityraised' else 'moneyraised_win3_updated'
    out[c]=rows.groupby('firm_id').amount.agg(amount_total).reindex(out.index)
    provenance[c]='Original deal source, original VDyear+1..+3; no round/undisclosed = missing'
# Retain legacy moneyraised_win3 as requested; updated comparable DV has new name.

print('Reading current status source...',flush=True)
book=pd.read_excel(ROOT/'2010 2015 Crunchbase deals merged_v4_series-updated.xlsx',header=1,usecols=['Organization Name','Funding Status','Operating Status','IPO Status','IPO Date'])
book['name_key']=book['Organization Name'].map(key)
book=book.groupby('name_key',sort=False).first()
assert ref.name_key.isin(book.index).all()
statuses=[]
for r in ref.itertuples():
    src=book.loc[r.name_key]; le=legacy.loc[r.firm_id]
    typ=str(le.exittype2).strip().lower(); ey=le.exityear2
    date=pd.to_datetime(src['IPO Date'],errors='coerce'); date_str=''
    if str(src['Funding Status']).upper()=='M&A':
        status='merged' if typ=='merged' else 'acquired'; year=ey if typ in ['merged','acquired'] else np.nan
    elif str(src['Funding Status']).upper()=='IPO' or str(src['IPO Status']).lower()=='public':
        status='public'; year=float(date.year) if pd.notna(date) else np.nan
        date_str=date.strftime('%Y-%m-%d') if pd.notna(date) else ''
    elif str(src['Operating Status']).lower()=='closed':
        status='defunct'; year=ey if typ=='closed' else np.nan
    else: status='private'; year=np.nan
    # Preserve raw event status. Do not turn pre-reference exits into survivors.
    statuses.append((r.firm_id,status,year,date_str,int(status in ['acquired','merged']),int(status=='public'),int(status=='defunct')))
st=pd.DataFrame(statuses,columns=['firm_id','status','status_year','status_date','m_a','ipo','defunct']).set_index('firm_id')
for c in st: out[c]=st[c]; provenance[c]='Current Crunchbase status + ORIGINAL legacy event dates; undated events remain missing'
out['status_pre_reference']=((out.status_year<=base.VDyear)&out.status_year.notna()).astype('int8')

print('Recovering available annual revenue for the additional original firms...',flush=True)
pb=pd.read_csv('C:/Users/user/Downloads/pb_deal_finance.csv',usecols=['companyid','companyname','fiscalyear','revenue'],low_memory=False)
pb['name_key']=pb.companyname.map(key)
unique=pb.groupby('name_key').companyid.nunique()
pb=pb[pb.name_key.isin(unique[unique.eq(1)].index)]
pb=pb.merge(ref[['firm_id','OrganizationName','name_key','VDyear']],on='name_key',how='inner',validate='many_to_one')
pb=pb[~pb.OrganizationName.isin(['Lemonade','Meta View','R.e.d.d.'])]
pb['event']=pd.to_numeric(pb.fiscalyear,errors='coerce')-pb.VDyear
pb['revenue']=pd.to_numeric(pb.revenue,errors='coerce')
for t in (1,2,3):
    for fid,z in pb[pb.event.eq(t)&pb.revenue.notna()].groupby('firm_id'):
        vals=np.unique(np.round(z.revenue.astype(float),6))
        if len(vals)==1 and out.at[fid,'supplement_same_reference']==0:
            out.at[fid,f'revenue_t{t}']=float(vals[0])*1e6
            out.at[fid,f'revenue_year_t{t}']=base.at[fid,'VDyear']+t
            out.at[fid,f'revenue_src_t{t}']='pb_deal_finance.csv'
            out.at[fid,f'revenue_basis_t{t}']='PB fiscalyear; USDm inferred; period unverified'

print('Reaggregating cached application-level innovation inputs...',flush=True)
g=win[win.ultimately_granted.eq(1)].copy()
g['primary_grant_patent_id']=g.grant_patent_ids.map(lambda x:float(re.findall(r'\d+',str(x))[0]) if re.findall(r'\d+',str(x)) else np.nan)
g['no_citation']=g.fwd_raw_total.eq(0).astype(int)
out['no_citation_share_win3']=g.groupby('firm_id').no_citation.mean().reindex(out.index)
oldapp=pd.read_csv(ROOT/'outputs/innovation_measures_2820/granted_application_innovation_measures.csv',dtype={'application_id':str},low_memory=False)
cachecols={'gunning_fog':'gunning_fog_mean_win3','automated_readability_index':'ari_mean_win3','neg_flesch_reading':'neg_flesch_mean_win3','number_figures':'figures_mean_win3','number_sheets':'sheets_mean_win3','number_claims':'claims_mean_win3','independent_claims':'indep_claims_mean_win3','dependent_claims':'dep_claims_mean_win3','description_word_count':'description_words_mean_win3'}
patcache=oldapp[['primary_grant_patent_id']+list(cachecols)].drop_duplicates('primary_grant_patent_id')
gg=g.merge(patcache,on='primary_grant_patent_id',how='left',validate='many_to_one')
for source,col in cachecols.items():
    computed=gg.groupby('firm_id')[source].mean()
    # For companies not in the earlier sample, do not report partial-portfolio
    # means as though all relevant patent text had been collected.
    counts=gg.groupby('firm_id')[source].count()
    totals=gg.groupby('firm_id').size()
    full=counts.eq(totals)
    fresh=computed.where(full).reindex(out.index)
    use=out.supplement_same_reference.eq(0)
    out.loc[use,col]=fresh[use]
    provenance[col]='Existing same-reference values; otherwise complete cached patent-text portfolios only'
out['readability_patents_missing']=gg.groupby('firm_id').gunning_fog.apply(lambda x:x.isna().sum()).reindex(out.index,fill_value=0)
out['readability_patents_expected']=g.groupby('firm_id').size().reindex(out.index,fill_value=0)
aliases={'nocite_win3':'no_citation_share_win3','breakthrough_win3':'breakthrough_patent_share_win3','desc_words_win3':'description_words_mean_win3','fog_win3':'gunning_fog_mean_win3','ari_win3':'ari_mean_win3','neg_flesch_win3':'neg_flesch_mean_win3','figures_win3':'figures_mean_win3','sheets_win3':'sheets_mean_win3','claims_win3':'claims_mean_win3','ind_claims_win3':'indep_claims_mean_win3','dep_claims_win3':'dep_claims_mean_win3'}
for alias,src in aliases.items(): out[alias]=out[src]

# Keep supplemental coverage visible. Do not treat unknown/uncollected records
# as zero innovation, zero revenue, no exit, or an observed baseline portfolio.
out['innovation_uncollected']=((out.supplement_same_reference==0)&(out.readability_patents_missing>0)).astype('int8')
newonly=out.supplement_same_reference.eq(0)
audit_cols=['status','status_year','revenue_t1','revenue_t2','revenue_t3','gunning_fog_mean_win3','newpat_win3','oldpat_win3','newcpc_win3','cite_breadth_win3','self_citations_total_win3']
audit={c:{'observed_all':int(out[c].notna().sum()),'observed_nonshared':int(out.loc[newonly,c].notna().sum())} for c in audit_cols}
audit.update({'firms':2820,'exact_reference_reused':int((~newonly).sum()),'nonshared_or_changed_reference':int(newonly.sum()),'patent_text_uncollected_firms':int(out.innovation_uncollected.sum()),'undated_exit_firms':int((out.status.ne('private')&out.status_year.isna()).sum())})
print(json.dumps(audit,indent=2),flush=True)

# Existing variables are not overwritten by the supplement. Explicitly refreshed
# supplemental columns may already exist on a repeated run; drop only those.
out=out.drop(columns=[c for c in out if c in legacy.columns],errors='ignore')
for c in out.select_dtypes(include=['object','string']): out[c]=out[c].fillna('').astype(str)
with tempfile.TemporaryDirectory(prefix='vd_full_original2820_') as temp:
    temp=Path(temp); supplement=temp/'supplement.dta'; script=temp/'merge.do'
    out.reset_index().to_stata(supplement,write_index=False,version=118)
    drop='\n'.join('capture drop '+c for c in out.columns)
    script.write_text(f'''version 19
clear all
set more off
set linesize 255
log using "{temp.as_posix()}/merge.log", text replace
use "{TARGET.as_posix()}", clear
{drop}
merge 1:1 firm_id using "{supplement.as_posix()}", assert(match) nogen
assert _N==2820
label variable innovation_source_covered "Earlier innovation collection covers this exact firm and reference year"
label variable innovation_uncollected "Additional patent text required; missing is NOT zero innovation"
label variable priorpatentdummy_VD "Original 260122 patentdummybyfiling; preserved moderator"
label variable moneyraised_win3_updated "All financing t+1..t+3 rebuilt from deal source; none/undisclosed missing"
notes: Complete do-file schema added. Missing supplemental source data not imputed.
notes: Original moneyraised_win3 retained. Rebuilt comparable amount is moneyraised_win3_updated.
notes: Innovation source coverage differs from original 2820 membership; consult coverage audit.
sort firm_id
save "{TARGET.as_posix()}", replace
log close
exit, clear
''',encoding='utf-8')
    subprocess.run(['C:/Program Files/StataNow19/StataSE-64.exe','/e','do',str(script)],creationflags=subprocess.CREATE_NO_WINDOW,timeout=180)
    log=(temp/'merge.log').read_text(errors='replace')
    assert not re.search(r'^r\(\d+\);',log,re.M),log
saved=pd.read_stata(TARGET,convert_categoricals=False).set_index('firm_id')
pd.testing.assert_frame_equal(saved[legacy.columns].sort_index(),legacy.sort_index(),check_dtype=False,check_exact=True)
assert set(extra).issubset(saved.columns)
(PKG/'original2820_full_schema_coverage.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
report=ref.set_index('firm_id')[['OrganizationName','VDyear']].join(out[['supplement_same_reference','innovation_uncollected','readability_patents_missing','readability_patents_expected']+audit_cols])
report.to_csv(PKG/'original2820_supplement_coverage.csv',encoding='utf-8-sig')
print('Saved',len(saved),'firms;',len(saved.columns),'columns; all original columns unchanged.',flush=True)
