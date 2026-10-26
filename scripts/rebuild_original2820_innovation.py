"""Rebuild original-cohort innovation measurements; never write rematched data.

Stages are resumable. Production merge is a separate, validated final step.
"""
from pathlib import Path
from collections import defaultdict
import argparse, inspect, json, pickle, re, shutil
import pandas as pd
import numpy as np
import construct_polidoro_yang_measures as py

ROOT=Path(__file__).resolve().parents[1]
PKG=ROOT/'outputs/psm_final_2820_package'
OUT=ROOT/'outputs/innovation_original2820_rebuild_20261020'
OUT.mkdir(exist_ok=True)
PROD=PKG/'table3_original_2820_cross_section_v2.dta'
DO=PKG/'RUN_TABLE3_PATENT_APPLICATION_WIN3_v2.do'
OLD=ROOT/'outputs/innovation_measures_2820'
STEM=OUT/'staging_original2820'

def setup():
    backup=PKG/'backups/before_innovation_rebuild_20261020'
    backup.mkdir(parents=True,exist_ok=True)
    for p in [PROD,DO]:
        if not (backup/p.name).exists(): shutil.copy2(p,backup/p.name)
    if not STEM.with_suffix('.dta').exists():
        shutil.copy2(PROD,STEM.with_suffix('.dta'))
        d=pd.read_stata(PROD,convert_categoricals=False)
        assert len(d)==2820 and d.firm_id.is_unique
        d.to_csv(STEM.with_suffix('.csv'),index=False)
    py.TARGET=STEM
    py.OUT=OUT/'citations'; py.OUT.mkdir(exist_ok=True)
    for name in ['classification.pkl','verified_partner_aliases.csv']:
        if not (py.OUT/name).exists(): shutil.copy2(OLD/'polidoro_yang'/name,py.OUT/name)

def citations():
    setup()
    # Keep corrected, application-level startup links only. Broad startup-name
    # matching would reintroduce previously rejected namesakes. Partner matches
    # still use the documented exact names and source-backed parent aliases.
    if not (py.OUT/'ownership_augmented.pkl').exists():
        source=inspect.getsource(py.prepare_ownership)
        source=source.replace("                for fid in known_ids.get(aid,[]): owners[pid].add(fid)\n",'')
        source=source.replace("                if k in startup_keys: owners[pid].add(startup_keys[k])\n",'')
        exec(compile(source,'<corrected-union-only-startup-linkage>','exec'),py.__dict__)
        result=py.prepare_ownership()
        py.save_cache('ownership_augmented.pkl',result)
    source=inspect.getsource(py.construct)
    source=source.replace("dates[pid]<=int(g.reference_year.iloc[0])*10000+1231", "dates[pid]<int(g.reference_year.iloc[0])*10000+101")
    source=source.replace('            profile_counts[key]=(total,total_refs)',
        '            profile_counts[key]=(total,total_refs)\n            if total != total_refs: partner_profiles[key]=None')
    source=source.replace("'no_classified_backward_citations' if npre", "'no_complete_classified_backward_profile' if npre")
    exec(compile(source,'<strict-pretreatment-and-complete-partner-profiles>','exec'),py.__dict__)
    py.construct()

def text_stage():
    setup()
    import add_disclosure_claim_grant_measures as tx
    tx.CACHE=OUT/'patent_text_cache.csv'
    if not tx.CACHE.exists(): shutil.copy2(OLD/'patent_disclosure_claim_metrics_fast_cache.csv',tx.CACHE)
    d=pd.read_stata(PROD,convert_categoricals=False)
    apps=pd.read_csv(py.APPS,low_memory=False,dtype={'application_id':str})
    ref=d[['firm_id','OrganizationName','VDyear']].copy()
    ref['key']=ref.OrganizationName.map(tx.key)
    assert ref.key.is_unique
    apps['key']=apps.organization_name.map(tx.key)
    apps=apps.merge(ref[['key','firm_id','VDyear']],on='key',validate='many_to_one')
    apps['event_time']=apps.filing_year-apps.VDyear
    apps=apps.loc[apps.event_time.between(1,3)&apps.filing_year.le(2024)].copy()
    _,dates=pickle.load(open(py.OUT/'classification.pkl','rb'))
    grant_audit=pd.read_csv(py.OUT/'grant_date_audit.csv')
    withdrawn=set(grant_audit.loc[grant_audit.withdrawn.eq(1),'patent_id'])
    def primary_id(s):
        valid=[x for x in py.ids(s) if x<len(dates) and 0<dates[x]<=20241231 and x not in withdrawn]
        return min(valid,key=lambda x:(dates[x],x)) if valid else np.nan
    apps['primary_grant_patent_id']=apps.grant_patent_ids.map(primary_id)
    apps.to_csv(OUT/'original_window_applications.csv',index=False)
    pids=apps.loc[apps.ultimately_granted.eq(1),'primary_grant_patent_id'].dropna().astype(int)
    print('Original-window granted applications:',len(pids),'unique grant IDs:',pids.nunique(),flush=True)
    from concurrent.futures import ThreadPoolExecutor, as_completed
    cache=pd.read_csv(tx.CACHE)
    words_path=OUT/'description_word_count_cache.csv'
    if not words_path.exists(): shutil.copy2(OLD/'description_word_count_cache.csv',words_path)
    words=pd.read_csv(words_path)
    # Fetch once for either missing text or missing length. Existing successful
    # patent-level source measurements may be reused; firm means may not.
    done=set(cache.loc[cache.metric_status.eq('ok'),'patent_id']) & set(words.loc[words.description_status.eq('ok'),'patent_id'])
    todo=sorted(set(pids)-done)
    source=inspect.getsource(tx.fetch_metrics)
    source=source.replace('"patent_id": int(patent_id),\n                "gunning_fog"',
        '"patent_id": int(patent_id),\n                "description_word_count": len(re.findall(r"\\b[\\w]+(?:[-\u0027][\\w]+)*\\b", description, flags=re.UNICODE)),\n                "gunning_fog"')
    exec(compile(source,'<text-and-description-length>','exec'),tx.__dict__)
    print('Text/length retrieval required:',len(todo),flush=True)
    pending=[]
    def save_pending():
        nonlocal cache,words,pending
        if not pending:return
        u=pd.DataFrame(pending)
        cache=pd.concat([cache,u.drop(columns='description_word_count',errors='ignore')]).drop_duplicates('patent_id',keep='last')
        if 'description_word_count' not in u:u['description_word_count']=np.nan
        w=u[['patent_id','description_word_count','metric_status']].rename(columns={'metric_status':'description_status'})
        # Do not replace a previously successful word count after a failed fetch.
        w=w.loc[~w.patent_id.isin(set(words.loc[words.description_status.eq('ok'),'patent_id']))|w.description_status.eq('ok')]
        words=pd.concat([words,w]).drop_duplicates('patent_id',keep='last')
        cache.to_csv(tx.CACHE,index=False); words.to_csv(words_path,index=False); pending=[]
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures=[pool.submit(tx.fetch_metrics,int(pid)) for pid in todo]
        for i,f in enumerate(as_completed(futures),1):
            pending.append(f.result())
            if i%50==0:
                save_pending(); print(f'Text progress {i}/{len(todo)}',flush=True)
    save_pending()
    official=tx.read_patentsview_subset(tx.G_PATENT,pids,['patent_id','num_claims'])
    figures=tx.read_patentsview_subset(tx.G_FIGURES,pids,['patent_id','num_figures','num_sheets'])
    official.merge(figures,on='patent_id',how='outer',validate='one_to_one').to_csv(OUT/'official_claims_figures.csv',index=False)
    print('Text stage complete',flush=True)

def benchmark():
    """Full-universe, cutoff-corrected top-five-percent membership."""
    setup()
    maps,dates=pickle.load(open(py.OUT/'classification.pkl','rb'))
    classes,labels=maps['CPC3']
    path=OUT/'benchmark_members_2024.csv'
    if path.exists(): return
    counts=np.zeros(len(dates),dtype=np.int32)
    carry_src=None; carry_refs=set()
    for i,d in enumerate(py.chunks('g_us_patent_citation.tsv.zip',['patent_id','citation_patent_id'],1_500_000)):
        d=d.loc[d.patent_id.str.fullmatch(r'\d+')&d.citation_patent_id.str.fullmatch(r'\d+')].copy()
        d=d.astype({'patent_id':'int64','citation_patent_id':'int64'})
        d=d.loc[(d.patent_id<len(dates))&(d.citation_patent_id<len(dates))]
        d=d.drop_duplicates()
        if carry_src is not None:d=d.loc[~(d.patent_id.eq(carry_src)&d.citation_patent_id.isin(carry_refs))]
        if len(d):
            last=int(d.patent_id.iloc[-1]); refs=set(d.loc[d.patent_id.eq(last),'citation_patent_id'])
            if last==carry_src:refs|=carry_refs
            carry_src,carry_refs=last,refs
        src=d.patent_id.to_numpy(); dst=d.citation_patent_id.to_numpy()
        valid=(dates[src]>0)&(dates[src]<=20241231)&(dates[dst]>0)&(dates[dst]<=dates[src])
        np.add.at(counts,dst[valid],1)
        if i%10==0: print(f'2024 benchmark citation scan: {(i+1)*1500000:,}',flush=True)
    np.save(OUT/'forward_counts_2024.npy',counts)
    rows=[]
    for d in py.chunks('g_application.tsv.zip',['patent_id','filing_date']):
        d=d.loc[d.patent_id.str.fullmatch(r'\d+')].copy()
        d['patent_id']=d.patent_id.astype(int)
        d=d.loc[d.patent_id<len(dates)]
        d['filing_year']=pd.to_numeric(d.filing_date.str[:4],errors='coerce')
        pid=d.patent_id.to_numpy()
        valid=(dates[pid]>0)&(dates[pid]<=20241231)&(classes[pid]>=0)&d.filing_year.between(2010,2024).to_numpy()
        d=d.loc[valid,['patent_id','filing_year']]; pid=d.patent_id.to_numpy()
        d['cpc3']=[labels[c] for c in classes[pid]]; d['forward_count']=counts[pid]
        rows.append(d)
    u=pd.concat(rows).drop_duplicates('patent_id')
    u=u.sort_values(['filing_year','cpc3','forward_count','patent_id'],ascending=[True,True,False,True])
    u['rank']=u.groupby(['filing_year','cpc3']).cumcount()+1
    u['universe_n']=u.groupby(['filing_year','cpc3']).patent_id.transform('size')
    u['selected']=u['rank']<=np.ceil(.05*u.universe_n)
    u.loc[u.selected].to_csv(path,index=False)
    u.groupby(['filing_year','cpc3']).agg(universe_n=('patent_id','size'),selected_n=('selected','sum')).to_csv(OUT/'benchmark_cells_2024.csv')
    print('2024 benchmark complete:',len(u),'patents;',int(u.selected.sum()),'selected',flush=True)

def finalize_benchmark():
    """Remove withdrawn grants from the ranking universe; retain audit evidence."""
    setup()
    maps,dates=pickle.load(open(py.OUT/'classification.pkl','rb'))
    classes,labels=maps['CPC3']; counts=np.load(OUT/'forward_counts_2024.npy')
    excluded=[]
    for d in py.chunks('g_patent.tsv.zip',['patent_id','withdrawn']):
        hit=d.loc[d.withdrawn.eq('1')&d.patent_id.str.fullmatch(r'\d+')].copy()
        excluded.extend(hit.patent_id.astype(int).tolist())
    pd.DataFrame({'patent_id':excluded}).to_csv(OUT/'all_withdrawn_patents.csv',index=False)
    excluded=set(excluded);rows=[]
    for d in py.chunks('g_application.tsv.zip',['patent_id','filing_date']):
        d=d.loc[d.patent_id.str.fullmatch(r'\d+')].copy();d['patent_id']=d.patent_id.astype(int)
        d=d.loc[(d.patent_id<len(dates))&~d.patent_id.isin(excluded)]
        d['filing_year']=pd.to_numeric(d.filing_date.str[:4],errors='coerce')
        pid=d.patent_id.to_numpy()
        valid=(dates[pid]>0)&(dates[pid]<=20241231)&(classes[pid]>=0)&d.filing_year.between(2010,2024).to_numpy()
        d=d.loc[valid,['patent_id','filing_year']];pid=d.patent_id.to_numpy()
        d['cpc3']=[labels[c] for c in classes[pid]];d['forward_count']=counts[pid];rows.append(d)
    u=pd.concat(rows).drop_duplicates('patent_id').sort_values(['filing_year','cpc3','forward_count','patent_id'],ascending=[True,True,False,True])
    u['rank']=u.groupby(['filing_year','cpc3']).cumcount()+1
    u['universe_n']=u.groupby(['filing_year','cpc3']).patent_id.transform('size')
    u['selected']=u['rank']<=np.ceil(.05*u.universe_n)
    u.loc[u.selected].to_csv(OUT/'benchmark_members_2024.csv',index=False)
    u.groupby(['filing_year','cpc3']).agg(universe_n=('patent_id','size'),selected_n=('selected','sum')).to_csv(OUT/'benchmark_cells_2024.csv')
    print('Final benchmark:',len(u),'valid grants;',int(u.selected.sum()),'top5 members',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('stage',choices=['citations','text','setup','benchmark','finalize-benchmark'])
    stage=parser.parse_args().stage
    {'citations':citations,'text':text_stage,'setup':setup,'benchmark':benchmark,'finalize-benchmark':finalize_benchmark}[stage]()
