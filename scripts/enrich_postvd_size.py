from pathlib import Path
import pandas as pd
import numpy as np
import re, json, shutil, hashlib, sys
from datetime import datetime

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'outputs/psm_final_2820_package'
OUT=BASE/'postvd_size_research'
OUT.mkdir(exist_ok=True)
SOURCE=Path('C:/Users/user/Downloads/pb_deal_finance.csv')
def norm(x):
    return re.sub(r'[^a-z0-9]', '', str(x).casefold())
def prepare():
    d=pd.read_stata(BASE/'table3_current_2820_cross_section_v2.dta',convert_categoricals=False)
    p=pd.read_csv(SOURCE,low_memory=False)
    p['source_row']=np.arange(len(p))+2
    p['exact_key']=p.companyname.str.casefold().str.strip()
    d['exact_key']=d.OrganizationName.str.casefold().str.strip()
    p['name_key']=p.companyname.map(norm)
    d['name_key']=d.OrganizationName.map(norm)
    counts=p.groupby('name_key').companyid.nunique()
    exactcounts=p.groupby('exact_key').companyid.nunique()
    e=p[p.exact_key.isin(exactcounts[exactcounts.eq(1)].index)].merge(d[['firm_id','OrganizationName','VD','VDyear','exact_key']],on='exact_key',validate='many_to_one')
    e['match_method']='exact_casefold'
    rest=d[~d.firm_id.isin(e.firm_id)]
    n=p[p.name_key.isin(counts[counts.eq(1)].index)].merge(rest[['firm_id','OrganizationName','VD','VDyear','name_key']],on='name_key',validate='many_to_one')
    n['match_method']='normalized_unique'
    # Punctuation/spacing normalization can merge distinct businesses.
    rejected=n[n.OrganizationName.isin(['Lemonade','Meta View','R.e.d.d.'])].copy()
    rejected.to_csv(OUT/'pb_rejected_normalized_matches.csv',index=False)
    n=n[~n.OrganizationName.isin(['Lemonade','Meta View','R.e.d.d.'])]
    m=pd.concat([e,n],ignore_index=True)
    m['rel_year']=m.fiscalyear-m.VDyear
    m['deal_rel_year']=m.deal_year-m.VDyear
    m.to_csv(OUT/'pb_matched_all_records.csv',index=False)
    amb=p[p.name_key.isin(counts[counts.gt(1)].index)].merge(d[~d.firm_id.isin(m.firm_id)][['firm_id','OrganizationName','name_key']],on='name_key')
    amb.to_csv(OUT/'pb_ambiguous_name_records.csv',index=False)
    m[m.rel_year.between(1,3)].to_csv(OUT/'pb_window_records.csv',index=False)
    d[~d.firm_id.isin(m.firm_id)].drop(columns='name_key').to_csv(OUT/'pb_unmatched_firms.csv',index=False)
    print(json.dumps({'firms':len(d),'matched_firms':m.firm_id.nunique(),'ambiguous_firms':amb.firm_id.nunique(),'pb_revenue_window_firms':m.loc[m.rel_year.between(1,3)&m.revenue.notna(),'firm_id'].nunique(),'pb_revenue_window_rows':int((m.rel_year.between(1,3)&m.revenue.notna()).sum())}))
    print(m.loc[m.rel_year.between(1,3)&m.revenue.notna(),['OrganizationName','VDyear','fiscalyear','revenue']].drop_duplicates().head(40).to_string(index=False))
def update():
    from postvd_web_evidence import rows
    dta=BASE/'table3_current_2820_cross_section_v2.dta'
    csv=BASE/'table3_current_2820_cross_section_v2.csv'
    with pd.io.stata.StataReader(dta) as reader:
        labels=reader.variable_labels()
        vallabels=reader.value_labels()
        label=reader.data_label
        original=reader.read(convert_categoricals=False)
    origcsv=pd.read_csv(csv)
    assert len(original)==2820 and original.firm_id.is_unique
    assert set(origcsv.firm_id)==set(original.firm_id)
    # Read the current file at commit time to preserve other authorized work.
    m=pd.read_csv(OUT/'pb_matched_all_records.csv',low_memory=False)
    web=pd.DataFrame(rows).merge(original[['firm_id','OrganizationName','VDyear']],on='OrganizationName',validate='many_to_one')
    web['rel_year']=web.observed_year-web.VDyear
    web['in_window']=web.rel_year.between(1,3)
    web.to_csv(OUT/'web_observations.csv',index=False)
    x=pd.DataFrame(index=original.firm_id)
    mapping=m[['firm_id','companyid','companyname','match_method']].drop_duplicates('firm_id').set_index('firm_id')
    x['pb_companyid']=mapping.companyid
    x['pb_companyname']=mapping.companyname
    x['pb_name_match']=mapping.match_method
    conflicts=[]
    selected=[]
    fields=['revenue','grossprofit','netincome','ebitda','totaldebt']
    for t in (1,2,3):
        window=m[m.rel_year.eq(t)]
        for metric in fields:
            col=f'pb_{metric}_raw_t{t}'
            x[col]=np.nan
            if metric=='revenue':
                x[f'pb_rev_nvals_t{t}']=0
                x[f'pb_rev_min_raw_t{t}']=np.nan
                x[f'pb_rev_max_raw_t{t}']=np.nan
                x[f'pb_rev_rows_t{t}']=''
                x[f'pb_rev_dealdate_t{t}']=''
            for fid,g in window[window[metric].notna()].groupby('firm_id'):
                values=np.unique(np.round(g[metric].astype(float),6))
                if len(values)==1:
                    x.loc[fid,col]=float(g[metric].iloc[0])
                else:
                    conflicts.append({'firm_id':fid,'t':t,'metric':metric,'values_raw':json.dumps(values.tolist()),'source_rows':';'.join(g.source_row.astype(str))})
                if metric=='revenue':
                    x.loc[fid,f'pb_rev_nvals_t{t}']=len(values)
                    x.loc[fid,f'pb_rev_min_raw_t{t}']=min(values)
                    x.loc[fid,f'pb_rev_max_raw_t{t}']=max(values)
                    x.loc[fid,f'pb_rev_rows_t{t}']=';'.join(g.source_row.astype(str))
                    x.loc[fid,f'pb_rev_dealdate_t{t}']=';'.join(sorted(g.dealdate.dropna().unique()))
        for metric in ('employees','revenue'):
            stem=f'{metric}_t{t}'
            x[stem]=np.nan
            x[f'{metric}_year_t{t}']=np.nan
            x[f'{metric}_src_t{t}']=''
            x[f'{metric}_basis_t{t}']=''
            x[f'{metric}_date_t{t}']=''
            if metric=='revenue':
                ok=x[f'pb_revenue_raw_t{t}'].notna()
                x.loc[ok,stem]=x.loc[ok,f'pb_revenue_raw_t{t}']*1e6
                years=original.set_index('firm_id').VDyear+t
                x.loc[ok,f'{metric}_year_t{t}']=years[ok]
                x.loc[ok,f'{metric}_src_t{t}']='pb_deal_finance.csv'
                x.loc[ok,f'{metric}_basis_t{t}']='PB fiscalyear; USDm inferred; period unverified'
                # Deal date is not the financial measurement date. Retained in pb_rev_dealdate.
            candidates=web[web.rel_year.eq(t)&web.metric.eq(metric)]
            for fid,g in candidates.groupby('firm_id'):
                eligible=g[g.basis.isin(['reported','approximate','management_claim'])].sort_values('observed_date')
                if not eligible.empty:
                    r=eligible.iloc[-1]
                    x.loc[fid,stem]=r.value
                    x.loc[fid,f'{metric}_year_t{t}']=r.observed_year
                    x.loc[fid,f'{metric}_src_t{t}']=r.source_url
                    x.loc[fid,f'{metric}_basis_t{t}']=r.basis
                    x.loc[fid,f'{metric}_date_t{t}']=r.observed_date
                    selected.append(r.to_dict())
        x[f'emp_est_t{t}']=np.nan
        x[f'emp_lower_t{t}']=np.nan
        x[f'emp_upper_approx_t{t}']=np.nan
        x[f'emp_fte_t{t}']=np.nan
        x[f'emp_aux_year_t{t}']=np.nan
        x[f'emp_aux_src_t{t}']=''
        for _,r in web[web.rel_year.eq(t)&web.metric.eq('employees')].iterrows():
            cols={'third_party_estimate':f'emp_est_t{t}','lower_bound':f'emp_lower_t{t}','upper_approximate':f'emp_upper_approx_t{t}','reported_fte':f'emp_fte_t{t}'}
            if r.basis in cols:
                x.loc[r.firm_id,cols[r.basis]]=r.value
                x.loc[r.firm_id,f'emp_aux_year_t{t}']=r.observed_year
                x.loc[r.firm_id,f'emp_aux_src_t{t}']+=((' | ' if x.loc[r.firm_id,f'emp_aux_src_t{t}'] else '')+r.basis+': '+r.source_url)
    x['size_retrieved']='2026-10-15'
    x['pb_unit_status']='USD million inferred from cross-check; no export metadata'
    x['employees_nyears']=x[[f'employees_t{t}' for t in (1,2,3)]].notna().sum(axis=1)
    x['revenue_nyears']=x[[f'revenue_t{t}' for t in (1,2,3)]].notna().sum(axis=1)
    # Explicit status distinguishes an unsearched firm from a negative search result.
    searched=['123Compliance','15Five','1World Online','2Morrow','2nd Watch','2ULaundry','365 Data Centers','3AM Innovations','3D Cloud by Marxent','410 Medical','6sense','88rising','4C Insights','908 Devices','9Lenses','Acalvio Technologies','Actively Learn','Datadog','Duo Security','Citus Data','DataStax','CloudBees','Credit Sesame','Absci','Acutus Medical','AdAdapted','AdaptHealth','Domo','Eargo','EverTrue','Ezoic','CapLinked','Contently','Comprehend Systems','DealCloud','Fonteva','Foodsmart','friendbuy','Glooko','Tipalti','HomeLight','Udacity','SingleStore']
    searched+=['Nimbix','Optimizely','Lighter Capital','Runwise','Rover','Payveris','Cloudability']
    searched+=['GreyOrange','JobNimbus','Saviynt','Fundrise']
    searched_ids=original.loc[original.OrganizationName.isin(searched),'firm_id']
    x['size_web_status']='not_yet_searched'
    x.loc[x.index.isin(searched_ids),'size_web_status']='searched_no_eligible_point'
    x.loc[x.index.isin(web.loc[web.in_window,'firm_id']),'size_web_status']='evidence_found_see_audit'
    # No zero imputation, no averaging conflicting source records, no current-to-past backfill.
    for c in x.select_dtypes(include=['object','str']):
        x[c]=x[c].fillna('').astype(str)
    oldcols=[c for c in original if c not in x.columns]
    result=original[oldcols].merge(x.reset_index(),on='firm_id',how='left',validate='one_to_one',sort=False)
    for c in oldcols:
        pd.testing.assert_series_equal(result[c],original[c],check_dtype=True)
    for t in (1,2,3):
        for metric in ('employees','revenue'):
            observed=result[f'{metric}_t{t}'].notna()
            assert (result.loc[observed,f'{metric}_year_t{t}']==result.loc[observed,'VDyear']+t).all()
    for c in x.columns:
        labels[c]=({'pb_unit_status':'PB monetary fields: USD million inferred, not export-metadata verified','size_web_status':'Web research progress, not a missing-value reason','size_retrieved':'Local retrieval date, distinct from measurement year'}.get(c,c.replace('_',' ')))[:80]
    # Preserve original Stata value-label assignments through categorical metadata mapping.
    with pd.io.stata.StataReader(dta) as rd:
        rd.read(1,convert_categoricals=False)
        value_labels={var:vallabels[lab] for var,lab in zip(rd._varlist,rd._lbllist) if lab in vallabels}
    tmpd=OUT/'validated_update.dta'
    tmpc=OUT/'validated_update.csv'
    result.to_stata(tmpd,write_index=False,version=118,variable_labels=labels,value_labels=value_labels,data_label=label)
    # Preserve CSV row order and original columns/values, adding only research fields.
    keep=[c for c in origcsv if c not in x.columns]
    csvresult=origcsv[keep].merge(x.reset_index(),on='firm_id',how='left',sort=False,validate='one_to_one')
    csvresult.to_csv(tmpc,index=False)
    reloaded=pd.read_stata(tmpd,convert_categoricals=False)
    pd.testing.assert_frame_equal(result,reloaded,check_dtype=False)
    checkcsv=pd.read_csv(tmpc,keep_default_na=False)
    for c in csvresult:
        if pd.api.types.is_numeric_dtype(csvresult[c]):
            np.testing.assert_allclose(pd.to_numeric(checkcsv[c],errors='coerce'),csvresult[c],equal_nan=True)
        else:
            assert checkcsv[c].tolist()==csvresult[c].fillna('').astype(str).tolist(),c
    assert len(pd.read_csv(tmpc))==2820
    backup=BASE/'backups'/('before_postvd_size_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
    backup.mkdir(parents=True)
    for f in (dta,csv): shutil.copy2(f,backup/f.name)
    shutil.copy2(tmpd,dta)
    shutil.copy2(tmpc,csv)
    pd.DataFrame(conflicts).to_csv(OUT/'pb_conflicting_values.csv',index=False)
    long=[]
    for _,r in result.iterrows():
        for t in (1,2,3):
            long.append(dict(firm_id=r.firm_id,OrganizationName=r.OrganizationName,VD=r.VD,VDyear=r.VDyear,t=t,year=r.VDyear+t,employees=r[f'employees_t{t}'],employees_source=r[f'employees_src_t{t}'],employees_basis=r[f'employees_basis_t{t}'],revenue_usd=r[f'revenue_t{t}'],revenue_source=r[f'revenue_src_t{t}'],revenue_basis=r[f'revenue_basis_t{t}'],pb_revenue_raw=r[f'pb_revenue_raw_t{t}'],pb_revenue_nvalues=r[f'pb_rev_nvals_t{t}']))
    pd.DataFrame(long).to_csv(OUT/'postvd_size_firm_year.csv',index=False)
    summary={'n_firms':len(result),'pb_matched_firms':int(result.pb_companyid.ne('').sum()),'revenue_firms':int(result.revenue_nyears.gt(0).sum()),'revenue_firm_years':int(result.revenue_nyears.sum()),'employees_firms':int(result.employees_nyears.gt(0).sum()),'employees_firm_years':int(result.employees_nyears.sum()),'web_searched_firms':int(result.size_web_status.ne('not_yet_searched').sum()),'web_evidence_rows':len(web),'pb_conflict_metric_firm_years':len(conflicts),'backup':str(backup),'unit':'USD million inferred, not metadata verified','web_research_complete':False}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':
    update() if '--update' in sys.argv else prepare()
