"""Strict original-sample aggregation with explicit missing-data reasons.

No rematched firm-level measurement is used. Run after the three raw stages.
This writes a validated update file, NOT the production DTA.
"""
from pathlib import Path
from collections import Counter,defaultdict
import json,pickle,re
import numpy as np
import pandas as pd
from rebuild_original2820_innovation import ROOT,OUT,PROD,py
from prepare_innovation_analysis import ALIASES

STATUS={0:'observed',1:'no_post_granted_patent',2:'incomplete_three_year_window',
        3:'text_or_claim_data_unavailable',4:'incomplete_technology_classification',
        5:'no_observed_pre_reference_granted_portfolio',6:'no_citations_denominator',
        7:'no_usable_partner_portfolio',8:'incomplete_source_coverage',
        9:'no_verified_patent_link_in_corrected_source',10:'claim_count_conflict'}

def key(x):return re.sub('[^a-z0-9]','',str(x).lower())

def main():
    old=pd.read_stata(PROD,convert_categoricals=False)
    assert len(old)==2820 and old.firm_id.is_unique
    a=pd.read_csv(OUT/'original_window_applications.csv',dtype={'application_id':str},low_memory=False)
    assert not a.duplicated(['firm_id','application_id']).any()
    p=pd.read_csv(OUT/'citations/ultimately_granted_patent_measures.csv',dtype={'application_id':str})
    assert not p.duplicated(['firm_id','patent_id']).any()
    maps,dates=pickle.load(open(OUT/'citations/classification.pkl','rb'))
    cls,labels=maps['CPC3']
    # One patent representation per application, consistent with application DV.
    p=p.sort_values(['firm_id','application_id','grant_date','patent_id'])
    duplicate_documents=p.loc[p.duplicated(['firm_id','application_id'],keep=False)]
    duplicate_documents.to_csv(OUT/'multiple_grant_documents_audit.csv',index=False)
    p=p.drop_duplicates(['firm_id','application_id'])
    w=p.loc[p.event_time.between(1,3)].copy()
    assert w.grant_date.le(20241231).all()
    text=pd.read_csv(OUT/'patent_text_cache.csv')
    words=pd.read_csv(OUT/'description_word_count_cache.csv')
    official=pd.read_csv(OUT/'official_claims_figures.csv')
    assert text.patent_id.is_unique and words.patent_id.is_unique and official.patent_id.is_unique
    w=w.merge(text,on='patent_id',how='left',validate='many_to_one')
    w=w.merge(words,on='patent_id',how='left',validate='many_to_one')
    w=w.merge(official,on='patent_id',how='left',validate='many_to_one')
    # Breadth is a COUNT of cited fields: a verified empty citation list is 0.
    # Diversity/HHI ratios, by contrast, are undefined with an empty denominator.
    w.loc[w.backward_citations.eq(0),'bc_technological_breadth']=0.0
    for c in ['gunning_fog','automated_readability_index','neg_flesch_reading','independent_claims','dependent_claims']:
        w.loc[w.metric_status.ne('ok'),c]=np.nan
    w.loc[w.description_status.ne('ok'),'description_word_count']=np.nan
    # A failed/partial claim parser is NOT a genuine zero independent-claim count.
    claims_ok=w.metric_status.eq('ok')&w.number_claims.eq(w.num_claims)&w.number_claims.gt(0)&w.independent_claims.gt(0)
    w.loc[~claims_ok,['firm_id','OrganizationName','application_id','patent_id','number_claims','num_claims','independent_claims','dependent_claims','metric_status']].to_csv(OUT/'claim_count_conflicts.csv',index=False)
    w.loc[w.num_figures.isna()|w.num_sheets.isna(),['firm_id','OrganizationName','application_id','patent_id','num_figures','num_sheets']].to_csv(OUT/'official_drawing_data_missing.csv',index=False)
    w.loc[~claims_ok,['independent_claims','dependent_claims']]=np.nan
    assert np.allclose((w.independent_claims+w.dependent_claims).dropna(),w.loc[claims_ok,'num_claims'])
    w['ln_description_words']=np.log(w.description_word_count.where(w.description_word_count.gt(0)))
    fullcounts=np.load(OUT/'forward_counts_2024.npy')
    # Independent full-universe citation scan must match cohort-targeted scan.
    np.testing.assert_array_equal(w.forward_citations.to_numpy(),fullcounts[w.patent_id.to_numpy()])
    members=pd.read_csv(OUT/'benchmark_members_2024.csv')
    cells=pd.read_csv(OUT/'benchmark_cells_2024.csv')
    benchmark_cells=set(zip(cells.filing_year,cells.cpc3))
    selected=set(members.patent_id)
    w['no_citation']=w.forward_citations.eq(0).astype(float)
    w['breakthrough']=np.where([(y,c) in benchmark_cells for y,c in zip(w.filing_year,w.primary_class)],w.patent_id.isin(selected).astype(float),np.nan)
    # Fixed baseline from corrected original firm/application links, not a
    # fresh broad name match that could reintroduce known namesake errors.
    universe=pd.read_csv(py.APPS,low_memory=False,dtype={'application_id':str})
    ref={key(r.OrganizationName):int(r.firm_id) for r in old.itertuples()}
    universe['firm_id']=universe.organization_name.map(key).map(ref)
    universe=universe.loc[universe.firm_id.notna()].copy()
    universe['firm_id']=universe.firm_id.astype(int)
    years=old.set_index('firm_id').VDyear.to_dict()
    withdrawn=set(pd.read_csv(OUT/'all_withdrawn_patents.csv').patent_id)
    base=defaultdict(Counter); nb=Counter(); linked=set(universe.firm_id)
    baseline_rows=[]
    for r in universe.loc[universe.ultimately_granted.eq(1)].itertuples():
        valid=[x for x in py.ids(r.grant_patent_ids) if x not in withdrawn and x<len(dates) and 0<dates[x]<=20241231]
        if not valid:continue
        pid=min(valid,key=lambda x:(dates[x],x))
        if dates[pid] < int(years[r.firm_id])*10000+101:
            nb[r.firm_id]+=1
            if cls[pid]>=0:base[r.firm_id][int(cls[pid])]+=1
            baseline_rows.append((r.firm_id,r.application_id,pid,int(dates[pid]),int(cls[pid])))
    pd.DataFrame(baseline_rows,columns=['firm_id','application_id','patent_id','grant_date','primary_class']).to_csv(OUT/'fixed_baseline_applications.csv',index=False)
    # Source-restricted baseline count: historical patent ownership is not inferred.
    partners=pd.read_csv(OUT/'citations/partner_coverage_audit.csv')
    partners_n=partners.groupby('firm_id').size(); partners_ok=partners.groupby('firm_id').usable.sum()
    partner_incomplete=set(partners.loc[partners.usable.eq(1)&partners.classification_coverage.lt(1),'firm_id'])
    groups={fid:z for fid,z in w.groupby('firm_id')}
    appgroups={fid:z for fid,z in a.groupby('firm_id')}
    rows=[]; audit=[]
    metric_map={
      'gunning_fog_mean_win3':'gunning_fog','ari_mean_win3':'automated_readability_index',
      'neg_flesch_mean_win3':'neg_flesch_reading','description_words_mean_win3':'description_word_count',
      'ln_description_words_mean_win3':'ln_description_words','figures_mean_win3':'num_figures',
      'sheets_mean_win3':'num_sheets','claims_mean_win3':'num_claims','indep_claims_mean_win3':'independent_claims',
      'dep_claims_mean_win3':'dependent_claims','no_citation_share_win3':'no_citation',
      'breakthrough_patent_share_win3':'breakthrough','patent_originality_win3':'patent_originality',
      'bc_technological_breadth_win3':'bc_technological_breadth','self_citations_win3':'self_citations',
      'patent_generality_win3':'patent_generality','originality_all_classes_win3':'originality_all_classes',
      'technological_distance_win3':'technological_distance'}
    citation_metrics={'patent_originality','patent_generality','originality_all_classes'}
    for r in old.itertuples():
        fid=r.firm_id; z=groups.get(fid,w.iloc[:0]); aa=appgroups.get(fid,a.iloc[:0]); n=len(z)
        complete=r.VDyear+3<=2024
        expected=int(aa.ultimately_granted.eq(1).sum())
        row={'firm_id':fid,'innov_window_complete':int(complete),'innov_link_observed':int(fid in linked),
             'innovation_source_covered':1,'innovation_granted_apps_win3':n,
             'readability_patents_expected':expected,'readability_patents_missing':expected-int(z.gunning_fog.notna().sum()),
             'innovation_uncollected':int(expected>z.gunning_fog.notna().sum()),
             'applications_filed_win3':len(aa),'applications_granted_win3':expected,
             'py_granted_patents_win3':n,'description_apps_measured_win3':int(z.description_word_count.notna().sum()),
             'py_originality_n_win3':int(z.patent_originality.notna().sum()),
             'py_generality_n_win3':int(z.patent_generality.notna().sum()),
             'py_distance_n_win3':int(z.technological_distance.notna().sum()),
             'partners_total_pre':int(partners_n.get(fid,0)),'partners_usable_pre':int(partners_ok.get(fid,0)),
             'win3_observed':int(complete),'base_patents':nb[fid],'base_cpc':len(base[fid]),
             'base_cpc_cov':sum(base[fid].values())/nb[fid] if nb[fid] else np.nan,
             'post_cpc_cov':z.primary_class.notna().mean() if n else np.nan}
        reasons={}
        def put(name,value,status=0,measured=None):
            if not complete:value,status=np.nan,2
            row[name]=value; reasons[name]=status
            audit.append({'firm_id':fid,'OrganizationName':r.OrganizationName,'VDyear':r.VDyear,
                'variable':name,'value':value,'status':status,'reason':STATUS[status],
                'post_applications_expected':expected,'post_applications_used':n,
                'patents_measured':measured})
        for dest,src in metric_map.items():
            v=z[src]; status=0; value=v.mean()
            if n==0:status=1
            elif n!=expected:status=8; value=np.nan
            elif src in citation_metrics:
                denom='forward_citations' if src=='patent_generality' else 'backward_citations'
                eligible=z[denom].gt(0)
                if not eligible.any():status=6;value=np.nan
                elif v[eligible].isna().any():status=4;value=np.nan
            elif src=='technological_distance':
                if not row['partners_usable_pre']:status=7;value=np.nan
                elif fid in partner_incomplete:status=4;value=np.nan
                elif not z.backward_citations.gt(0).any():status=6;value=np.nan
                elif v[z.backward_citations.gt(0)].isna().any():status=4;value=np.nan
            elif v.isna().any():
                status=4 if src in ['breakthrough','bc_technological_breadth'] else (3 if src in ['gunning_fog','automated_readability_index','neg_flesch_reading','description_word_count','ln_description_words','independent_claims','dependent_claims'] else 8)
                if src in ['independent_claims','dependent_claims'] and z.metric_status.eq('ok').all():status=10
                value=np.nan
            put(dest,value,status,int(v.notna().sum()))
        # A source-linked firm with no post-window patents has a count of zero,
        # not a mean of zero. Firms with no verified link at any date stay missing.
        self_status=0 if n==expected and fid in linked else (9 if fid not in linked else 8)
        put('self_citations_total_win3',float(z.self_citations.sum()) if self_status==0 else np.nan,self_status)
        search=z.search_in_partners_domains
        search_status=0 if row['partners_usable_pre'] else 7
        if fid in partner_incomplete:search_status=4
        if not n and fid not in linked:search_status=9
        elif search.isna().any() or n!=expected:search_status=8
        raw=search.sum() if search_status==0 else np.nan
        put('partner_search_raw_win3',raw,search_status)
        put('search_in_partners_domains_win3',np.log1p(raw),search_status)
        put('grant_rate_win3',expected/len(aa) if len(aa) else np.nan,0 if len(aa) else 1)
        b=base[fid]; baseline_valid=nb[fid]>0 and sum(b.values())==nb[fid]
        status=0
        if nb[fid]==0:status=5
        elif not baseline_valid or z.primary_class.isna().any():status=4
        elif n!=expected:status=8
        new=np.array([float(cls[int(pid)] not in b) for pid in z.patent_id])
        nv=float(new.sum()) if status==0 else np.nan
        put('newpat_win3',nv,status);put('oldpat_win3',n-nv,status)
        new_classes={int(cls[int(pid)]) for pid,flag in zip(z.patent_id,new) if flag}
        put('newcpc_win3',float(len(new_classes)) if status==0 else np.nan,status)
        put('newshare_win3',nv/n if n and status==0 else np.nan,status if status else (0 if n else 1))
        distance=np.mean([1-b.get(int(cls[int(pid)]),0)/np.sqrt(sum(x*x for x in b.values())) for pid in z.patent_id]) if n and status==0 else np.nan
        put('own_dist_win3',distance,status if status else (0 if n else 1))
        bt=z.backward_citations.sum()
        put('selfshare_win3',z.self_citations.sum()/bt if bt and n==expected else np.nan,0 if bt and n==expected else (6 if not bt else 8))
        for alias,(source,label) in ALIASES.items():
            row[alias]=row[source]
            row[alias+'_status']=reasons[source]
        row['novelty_status']=reasons['newpat_win3'];row['selftotal_status']=reasons['self_citations_total_win3']
        for name,source in [('ln_newpat_win3','newpat_win3'),('ln_oldpat_win3','oldpat_win3'),
              ('ln_selfcitations_win3hare_win3','self_citations_total_win3'),('ln_desc_words_win3','desc_words_win3'),
              ('ln_figures_win3','figures_win3'),('ln_sheets_win3','sheets_win3'),('ln_claims_win3','claims_win3')]:
            row[name]=np.log1p(row[source])
        rows.append(row)
    update=pd.DataFrame(rows)
    assert update.firm_id.tolist()==old.firm_id.tolist()
    assert all(len(c)<=32 for c in update.columns)
    observed=update.innov_window_complete.eq(1)
    for c in [x for x in metric_map]+['newpat_win3','oldpat_win3','newcpc_win3','self_citations_total_win3']:
        assert update.loc[~observed,c].isna().all(),c
    valid=update.newpat_win3.notna()
    np.testing.assert_array_equal((update.newpat_win3+update.oldpat_win3)[valid],update.py_granted_patents_win3[valid])
    for c in ['nocite_win3','breakthrough_win3','generality_win3','cite_diversity_win3','originality_win3','newshare_win3','selfshare_win3','grant_rate_win3']:
        assert update[c].dropna().between(-1e-12,1+1e-12).all(),c
    assert (update.readability_patents_missing>=0).all()
    audit=pd.DataFrame(audit)
    audit.to_csv(OUT/'firm_measure_status.csv',index=False,encoding='utf-8-sig')
    summary=audit.groupby(['variable','status','reason'],dropna=False).agg(firms=('firm_id','size'),zero_values=('value',lambda x:int(x.eq(0).sum()))).reset_index()
    summary.to_csv(OUT/'measurement_coverage.csv',index=False,encoding='utf-8-sig')
    w.to_csv(OUT/'patent_level_remeasured.csv',index=False,encoding='utf-8-sig')
    update.to_csv(OUT/'innovation_update.csv',index=False)
    value_labels={c:STATUS for c in update if c.endswith('_status')}
    vl={c:'Innovation audit: '+c for c in update if c.endswith('_status')}
    for alias,(_,label) in ALIASES.items():vl[alias]=label[:80]
    vl.update({'innovation_source_covered':'Original-cohort raw-source reconstruction attempted; NOT proof of no patents',
               'innov_link_observed':'At least one corrected patent application link observed at any date',
               'innov_window_complete':'Reference year + 3 <= 2024; otherwise innovation outcomes missing',
               'applications_filed_win3':'Observed linked applications in window; zero is source-record count',
               'applications_granted_win3':'Observed linked granted applications; zero is source-record count',
               'self_citations_total_win3':'Count of citations to corrected matched own patents; complete t+1..t+3',
               'self_citations_win3':'Mean citations to corrected matched own patents; complete t+1..t+3',
               'base_patents':'Corrected linked applications granted before reference year; fixed baseline',
               'base_cpc':'Distinct primary CPC3 in corrected linked pre-reference granted applications'})
    update.to_stata(OUT/'innovation_update.dta',write_index=False,version=118,variable_labels=vl,value_labels=value_labels)
    qa={'firms':len(update),'treated':int(old.VD.sum()),'window_apps':len(a),'window_granted_apps_expected':int(a.ultimately_granted.sum()),
        'window_granted_applications_measured':len(w),'incomplete_windows':int((~observed).sum()),
        'no_verified_link':int(update.innov_link_observed.eq(0).sum()),
        'raw_rebuild_all_firms':True,'citation_scans_reconcile':True,
        'missing_text_firms':int(update.innovation_uncollected.sum()),
        'text_patents_measured':int(w.gunning_fog.notna().sum()),
        'claim_count_conflicts':int((~claims_ok).sum()),
        'official_drawing_rows_missing':int((w.num_figures.isna()|w.num_sheets.isna()).sum()),
        'nonmissing':{c:int(update[c].notna().sum()) for c in list(ALIASES)+['newpat_win3','oldpat_win3','newcpc_win3','self_citations_total_win3']},
        'definitions':{'window':'Filing year reference+1 to reference+3; calendar complete through 2024 required',
         'unit':'Unique application, represented by earliest valid nonwithdrawn grant through 2024',
         'baseline':'Corrected linked own applications granted strictly before reference year; no broad name rematching',
         'citations':'Distinct numeric US utility grant citations, citing grant through 2024; future-to-past violations excluded',
         'benchmark':'Full granted universe through 2024; filing-year x primary CPC3; ceil(5%) ranks, patent-ID tie break',
         'means':'Complete measurement over all eligible window applications; no averaging an uncollected text subset',
         'zero':'Observed zero only when denominator/source eligible; no firm-level patent link is not proof of zero patents',
         'limits':'Grant selection/right truncation remains for recent filings. Fixed 2024 citation horizon not normalized. Static assignee links not independently fully adjudicated. Partner metrics use usable matched partner portfolios only.'}}
    (OUT/'validation.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
    print(json.dumps(qa,indent=2),flush=True)

if __name__=='__main__':main()
