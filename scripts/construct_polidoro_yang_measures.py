"""Reproducible patent/partner construction; no synthetic partner portfolios.

Stages are cached to make full-universe scans resumable. All six constructs use
the same selected technological classification; exact construction choices and
departures from Polidoro & Yang (2021) are recorded in methodology.json.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import json
import pickle
import re
import shutil
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\user\Documents\VD")
SOURCE = ROOT / 'outputs/patentsview_2024_full_cohort/source'
OUT = ROOT / 'outputs/innovation_measures_2820/polidoro_yang'
OUT.mkdir(parents=True, exist_ok=True)
TARGET = ROOT / 'outputs/psm_final_2820_package/table3_current_2820_cross_section_v2'
APPS = ROOT / 'outputs/csdid_union_corrected_3yr/application_level_union_corrected_visible_mismatches.csv'
BOOK = ROOT / '2010 2015 Crunchbase deals merged_v4_series-updated.xlsx'
CUTOFF = 20241231
METRICS = ['patent_originality', 'bc_technological_breadth', 'self_citations',
           'search_in_partners_domains', 'technological_distance', 'patent_generality']
SHORT_NAME_ALLOWLIST={'sony','3m','att','htc','acer','kddi','jsr','nsk','usaa','upmc','agc','brex'}

def ambiguous_partner(key):
    return (len(key)<=4 and key not in SHORT_NAME_ALLOWLIST) or key in {'merck'}

def log(s):
    print(datetime.now().strftime('%H:%M:%S'), s, flush=True)

def norm(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii','ignore').decode().lower()
    s = re.sub(r'[^a-z0-9]+', ' ', s).strip()
    while re.search(r'\s+(incorporated|inc|corporation|corp|limited|ltd|llc|llp|plc|co|company)$',s):
        s = re.sub(r'\s+(incorporated|inc|corporation|corp|limited|ltd|llc|llp|plc|co|company)$','',s)
    return re.sub(r'\s+','',s)

def ids(s):
    if pd.isna(s): return []
    return list(dict.fromkeys(int(x) for x in re.findall(r'(?<!\d)\d{6,9}(?!\d)',str(s))))

def chunks(name, cols, size=1_000_000):
    with zipfile.ZipFile(SOURCE/name) as z:
        with z.open(next(n for n in z.namelist() if n.endswith('.tsv'))) as f:
            yield from pd.read_csv(f, sep='\t', usecols=cols, dtype=str,
                                  keep_default_na=False, chunksize=size)

def save_cache(name,obj):
    with (OUT/name).open('wb') as f: pickle.dump(obj,f,protocol=5)

def cache(name):
    with (OUT/name).open('rb') as f: return pickle.load(f)

def extract_deals():
    path=OUT/'partner_deals.csv'
    dates_path=OUT/'all_round_dates.csv'
    if path.exists() and dates_path.exists(): return pd.read_csv(path,keep_default_na=False)
    target=pd.read_csv(TARGET.with_suffix('.csv'))
    lookup={norm(r.OrganizationName):(int(r.firm_id),int(r.VDyear),int(r.VD)) for r in target.itertuples()}
    records=[]; all_dates=[]
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(BOOK) as z:
        strings=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml'))] if 'xl/sharedStrings.xml' in z.namelist() else []
        with z.open('xl/worksheets/sheet1.xml') as f:
            for _,row in ET.iterparse(f,events=['end']):
                if not row.tag.endswith('}row'): continue
                values={}
                for c in row:
                    col=re.sub(r'\d','',c.attrib.get('r',''))
                    v=c.find('m:v',ns)
                    if v is not None:
                        val=v.text or ''
                        if c.attrib.get('t')=='s': val=strings[int(val)]
                    else: val=''.join(c.itertext())
                    values[col]=val
                k=norm(values.get('D',''))
                if k in lookup:
                    fid,year,treated=lookup[k]
                    try:
                        date=pd.Timestamp('1899-12-30')+pd.Timedelta(days=float(values.get('H','')))
                        dateint=int(date.strftime('%Y%m%d'))
                    except (ValueError,OverflowError): dateint=0
                    if dateint:
                        all_dates.append((fid,year,treated,dateint,values.get('K','')))
                    raw=values.get('CB','')
                    if dateint and dateint<=year*10000+1231 and raw:
                        # Crunchbase export separates investor names by comma.
                        for partner in re.split(r',\s*|;\s*',raw):
                            if not partner.strip() or norm(partner) in {'inc','llc','ltd','lp','llp'}: continue
                            records.append((fid,values.get('D'),year,treated,dateint,
                                values.get('K',''),partner.strip(),norm(partner),raw,values.get('CA','')))
                row.clear()
    d=pd.DataFrame(records,columns=['firm_id','OrganizationName','reference_year','VD','deal_date',
                                   'funding_type','partner_name','partner_key','raw_investors','lead_investors'])
    d.to_csv(path,index=False,encoding='utf-8-sig')
    pd.DataFrame(all_dates,columns=['firm_id','reference_year','VD','deal_date','funding_type']).drop_duplicates().to_csv(dates_path,index=False)
    log(f'Investor relationships: {len(d):,} deal-investor rows, {d.partner_key.nunique():,} investors')
    return d

def prepare_ownership():
    if (OUT/'ownership_augmented.pkl').exists(): return cache('ownership_augmented.pkl')
    if (OUT/'ownership.pkl').exists(): return cache('ownership.pkl')
    deals=extract_deals()
    target=pd.read_csv(TARGET.with_suffix('.csv'))
    startup_keys={norm(r.OrganizationName):int(r.firm_id) for r in target.itertuples()}
    partner_keys=set(deals.partner_key)
    # Reviewed parent relationships can be added without fuzzy name inference.
    aliases_path=OUT/'verified_partner_aliases.csv'
    aliases=pd.read_csv(aliases_path).fillna('') if aliases_path.exists() else pd.DataFrame(columns=['partner_key','assignee_name','source_url'])
    alias_keys=defaultdict(set)
    for r in aliases.itertuples():
        assert r.source_url, 'Parent mappings require a verification source'
        alias_keys[norm(r.assignee_name)].add(r.partner_key)
    apps=pd.read_csv(APPS,dtype={'application_id':str},low_memory=False)
    apps['firm_id']=apps.organization_name.map(norm).map(startup_keys)
    apps=apps.loc[apps.firm_id.notna() & apps.ultimately_granted.eq(1)].copy()
    apps['firm_id']=apps.firm_id.astype(int)
    apps['reference_year']=apps.firm_id.map(target.set_index('firm_id').VDyear)
    apps['event_time']=apps.filing_year-apps.reference_year
    rows=[]; owners=defaultdict(set); known_ids=defaultdict(set)
    for r in apps.itertuples():
        for pid in ids(r.grant_patent_ids):
            owners[pid].add(int(r.firm_id))
            if -4<=r.event_time<=4:
                rows.append((r.firm_id,r.organization_name,r.application_id,pid,r.filing_date,
                             int(r.filing_year),int(r.reference_year),int(r.event_time)))
        for aid in re.findall(r'[a-zA-Z0-9-]{20,}', str(r.legacy_assignee_ids)):
            known_ids[aid].add(int(r.firm_id))
    patents=pd.DataFrame(rows,columns=['firm_id','OrganizationName','application_id','patent_id',
                'filing_date','filing_year','reference_year','event_time']).drop_duplicates(['firm_id','patent_id'])
    partner_owners=defaultdict(set); match_records=[]
    names={'disambig_assignee_organization','raw_assignee_organization'}
    for file,namecol in [('g_assignee_disambiguated.tsv.zip','disambig_assignee_organization'),
                         ('g_assignee_not_disambiguated.tsv.zip','raw_assignee_organization')]:
        for i,d in enumerate(chunks(file,['patent_id','assignee_id',namecol])):
            uniques=d[namecol].unique()
            normalized={x:norm(x) for x in uniques if x}
            d['key']=d[namecol].map(normalized)
            hit=d.loc[d['key'].isin(partner_keys|set(startup_keys)|set(alias_keys)) | d.assignee_id.isin(known_ids)]
            for pid,aid,name,k in hit[['patent_id','assignee_id',namecol,'key']].itertuples(index=False,name=None):
                if not pid.isdigit(): continue
                pid=int(pid)
                for fid in known_ids.get(aid,[]): owners[pid].add(fid)
                if k in startup_keys: owners[pid].add(startup_keys[k])
                pkeys=({k} if k in partner_keys else set()) | alias_keys.get(k,set())
                for pk in pkeys:
                    partner_owners[pid].add(pk)
                    match_records.append((pk,aid,name,file))
            log(f'{file}: {(i+1)*1_000_000:,} rows examined, {len(partner_owners):,} partner patents')
    pd.DataFrame(match_records,columns=['partner_key','assignee_id','assignee_name','match_source']).drop_duplicates().to_csv(
        OUT/'partner_assignee_matches.csv',index=False,encoding='utf-8-sig')
    result=(patents,dict(owners),dict(partner_owners))
    save_cache('ownership.pkl',result)
    return result

def augment_ownership():
    if (OUT/'ownership_augmented.pkl').exists(): return cache('ownership_augmented.pkl')
    patents,owners,powners=prepare_ownership()
    aliases=pd.read_csv(OUT/'verified_partner_aliases.csv')
    partners=set(extract_deals().partner_key)
    mapping=defaultdict(set)
    for r in aliases.itertuples():
        if r.partner_key in partners: mapping[norm(r.assignee_name)].add(r.partner_key)
    matches=[]
    for file,col in [('g_assignee_disambiguated.tsv.zip','disambig_assignee_organization'),
                     ('g_assignee_not_disambiguated.tsv.zip','raw_assignee_organization')]:
        normal_cache={}
        for i,d in enumerate(chunks(file,['patent_id','assignee_id',col])):
            for x in d[col].unique():
                if x not in normal_cache: normal_cache[x]=norm(x)
            d['key']=d[col].map(normal_cache)
            hit=d.loc[d['key'].isin(mapping)]
            for pid,aid,name,k in hit[['patent_id','assignee_id',col,'key']].itertuples(index=False,name=None):
                if not pid.isdigit(): continue
                pid=int(pid)
                for pk in mapping[k]:
                    powners.setdefault(pid,set()).add(pk)
                    matches.append((pk,aid,name,'verified_parent_alias'))
            log(f'Parent mapping {file} {(i+1)*1_000_000:,}')
    existing=pd.read_csv(OUT/'partner_assignee_matches.csv')
    pd.concat([existing,pd.DataFrame(matches,columns=existing.columns)]).drop_duplicates().to_csv(
        OUT/'partner_assignee_matches.csv',index=False,encoding='utf-8-sig')
    result=patents,owners,powners
    save_cache('ownership_augmented.pkl',result)
    return result

def anchored_pairs():
    d=extract_deals()
    d=d.loc[~d.funding_type.isin(['Grant','Non-equity Assistance','Product Crowdfunding','Initial Coin Offering'])].copy()
    target=pd.read_csv(TARGET.with_suffix('.csv'))
    cutoffs={int(r.firm_id):int(r.VDyear)*10000+1231 for r in target.itertuples()}
    rounds=pd.read_csv(OUT/'all_round_dates.csv',keep_default_na=False)
    actual=rounds.loc[rounds.VD.eq(1)&rounds.funding_type.str.contains('debt',case=False,na=False)&
                 (rounds.deal_date//10000).eq(rounds.reference_year)].groupby('firm_id').deal_date.min()
    cutoffs.update({int(k):int(v) for k,v in actual.items()})
    d=d.loc[d.deal_date.le(d.firm_id.map(cutoffs))].copy()
    d['reference_date']=d.firm_id.map(cutoffs)
    pd.DataFrame([{'firm_id':int(r.firm_id),'reference_date':cutoffs[int(r.firm_id)],
                   'date_basis':'actual_first_debt_date' if r.firm_id in actual.index else 'reference_year_end'}
                  for r in target.itertuples()]).to_csv(OUT/'reference_dates.csv',index=False)
    return d[['firm_id','partner_key','reference_year','reference_date']].drop_duplicates()

def classification():
    if (OUT/'classification.pkl').exists():
        maps,dates=cache('classification.pkl')
        if not (OUT/'grant_date_audit.csv').exists():
            patents,_,_=prepare_ownership()
            wanted=set(patents.patent_id)
            hits=[]
            for d in chunks('g_patent.tsv.zip',['patent_id','patent_date','withdrawn']):
                d=d.loc[d.patent_id.isin({str(x) for x in wanted})]
                if len(d): hits.append(d)
            audit=pd.concat(hits,ignore_index=True)
            audit.to_csv(OUT/'grant_date_audit.csv',index=False)
            for r in audit.itertuples(): dates[int(r.patent_id)]=int(r.patent_date.replace('-',''))
            save_cache('classification.pkl',(maps,dates))
        return maps,dates
    maps={}; counts={}
    for scheme,file,seq,col in [('USPC','g_uspc_at_issue.tsv.zip','uspc_sequence','uspc_mainclass_id'),
                                ('CPC3','g_cpc_current.tsv.zip','cpc_sequence','cpc_class')]:
        arr=np.full(15_000_000,-1,dtype=np.int16); labels=[]; codes={}
        for i,d in enumerate(chunks(file,['patent_id',seq,col])):
            d=d.loc[d[seq].eq('0') & d.patent_id.str.fullmatch(r'\d+') & d[col].ne('')]
            if len(d):
                for label in d[col].unique():
                    if label not in codes: codes[label]=len(labels); labels.append(label)
                pid=d.patent_id.astype(np.int64).to_numpy()
                if pid.max()>=len(arr): arr=np.pad(arr,(0,int(pid.max()+1-len(arr))),constant_values=-1)
                arr[pid]=d[col].map(codes).to_numpy(dtype=np.int16)
            if i%5==0: log(f'{scheme}: {(i+1)*1_000_000:,} classification rows examined')
        maps[scheme]=(arr,labels)
        counts[scheme]=int((arr>=0).sum())
        log(f'{scheme}: {counts[scheme]:,} primary-class patents')
    dates=np.zeros(15_000_000,dtype=np.int32)
    for d in chunks('g_patent.tsv.zip',['patent_id','patent_date','withdrawn']):
        d=d.loc[d.patent_id.str.fullmatch(r'\d+')]
        pid=d.patent_id.astype(np.int64).to_numpy()
        if len(pid) and pid.max()>=len(dates): dates=np.pad(dates,(0,int(pid.max()+1-len(dates))))
        dates[pid]=pd.to_numeric(d.patent_date.str.replace('-','',regex=False),errors='coerce').fillna(0).to_numpy(np.int32)
    save_cache('classification.pkl',(maps,dates))
    return maps,dates

def scan_citations():
    if (OUT/'citation_stats.pkl').exists(): return cache('citation_stats.pkl')
    patents,owners,powners=augment_ownership()
    maps,dates=classification()
    all_pids=patents.patent_id.to_numpy(dtype=int)
    coverage={scheme:float(np.mean(arr[all_pids]>=0)) for scheme,(arr,labels) in maps.items()}
    # USPC is no longer assigned to modern utility patents. Use the modern CPC3
    # analogue consistently when USPC cannot describe at least 95% of the sample.
    scheme='USPC' if coverage['USPC']>=.95 else 'CPC3'
    arr,labels=maps[scheme]
    log(f'Classification coverage {coverage}; main scheme={scheme}')
    pairs=anchored_pairs()
    last_ref=pairs.groupby('partner_key').reference_date.max().to_dict()
    powners={pid:ps for pid,ps in powners.items() if 0<dates[pid]<=CUTOFF}
    powners={pid:{p for p in ps if p in last_ref and dates[pid]<=last_ref[p] and not ambiguous_partner(p)} for pid,ps in powners.items()}
    powners={pid:ps for pid,ps in powners.items() if ps}
    relevant=set(owners)|set(powners)
    n=max(len(dates),len(arr)); relevant_flag=np.zeros(n,dtype=bool); relevant_flag[list(relevant)]=True
    target_flag=np.zeros(n,dtype=bool); target_flag[all_pids]=True
    backward=defaultdict(Counter); forward=defaultdict(Counter)
    btotal=Counter(); ftotal=Counter(); self_count=Counter()
    partner_year=defaultdict(Counter); partner_year_tot=Counter()
    prev_pid=None; prev_refs=set(); processed=0; dedup_removed=0; seen_sources=set()
    # Official file is ordered by patent_id/citation_sequence. Assert grouping
    # at boundaries and retain prior-group references to deduplicate split chunks.
    for i,d in enumerate(chunks('g_us_patent_citation.tsv.zip',['patent_id','citation_patent_id'],1_500_000)):
        d=d.loc[d.patent_id.str.fullmatch(r'\d+') & d.citation_patent_id.str.fullmatch(r'\d+')].copy()
        d['src']=d.patent_id.astype(np.int64); d['dst']=d.citation_patent_id.astype(np.int64)
        src=d.src.to_numpy(); dst=d.dst.to_numpy()
        valid=(src<n)&(dst<n)
        d=d.loc[valid]; src=d.src.to_numpy(); dst=d.dst.to_numpy()
        keep=relevant_flag[src]|target_flag[dst]
        d=d.loc[keep,['src','dst']]
        current_sources=set(d.src)
        assert not ((current_sources & seen_sources)-({prev_pid} if prev_pid is not None else set())), 'Citation source reappeared noncontiguously; requires global deduplication'
        seen_sources.update(current_sources)
        before=len(d); d=d.drop_duplicates(); dedup_removed+=before-len(d)
        # Full-file sorting is not guaranteed; per-patent sets below ensure exact
        # deduplication for targets. Partner aggregation uses unique source/ref
        # pairs per chunk, with a carry-over set for the last source patent.
        if prev_pid is not None:
            d=d.loc[~(d.src.eq(prev_pid)&d.dst.isin(prev_refs))]
        if len(d):
            last=int(d.src.iloc[-1]); refs=set(d.loc[d.src.eq(last),'dst'])
            if last==prev_pid: refs|=prev_refs
            prev_pid,prev_refs=last,refs
        s=d.src.to_numpy(dtype=int); t=d.dst.to_numpy(dtype=int)
        # Retain old cited patents absent from g_patent: otherwise their missing
        # classes would silently disappear from the denominator and inflate QA.
        date_valid=(dates[s]>0)&(dates[s]<=CUTOFF)&((dates[t]==0)|(dates[t]<=dates[s]))
        d=d.loc[date_valid]; s=d.src.to_numpy(dtype=int); t=d.dst.to_numpy(dtype=int)
        b=d.loc[relevant_flag[s]].copy()
        b['class']=arr[b.dst.to_numpy(dtype=int)]
        # Collapsing to class counts avoids retaining millions of citation edges.
        for pid,cnt in b.groupby('src').size().items(): btotal[int(pid)]+=int(cnt)
        bg=b.loc[b['class']>=0].groupby(['src','class']).size()
        for (pid,c),cnt in bg.items():
            pid=int(pid); c=int(c); cnt=int(cnt)
            if pid in owners: backward[pid][c]+=cnt
            for partner in powners.get(pid,()): partner_year[(partner,int(dates[pid]))][c]+=cnt
        for pid,cnt in b.groupby('src').size().items():
            for partner in powners.get(int(pid),()): partner_year_tot[(partner,int(dates[int(pid)]))]+=int(cnt)
        for src,dst in b.loc[b.src.isin(owners),['src','dst']].itertuples(index=False,name=None):
            common=owners[int(src)] & owners.get(int(dst),set())
            for fid in common: self_count[(fid,int(src))]+=1
        f=d.loc[target_flag[t]].copy(); f['class']=arr[f.src.to_numpy(dtype=int)]
        for pid,cnt in f.groupby('dst').size().items(): ftotal[int(pid)]+=int(cnt)
        for (pid,c),cnt in f.loc[f['class']>=0].groupby(['dst','class']).size().items(): forward[int(pid)][int(c)]+=int(cnt)
        processed+=1_500_000
        log(f'Citation scan {processed:,} rows; {len(backward):,} startup patent profiles; {len(partner_year):,} partner-year profiles')
    result=dict(scheme=scheme,coverage=coverage,labels=labels,backward=dict(backward),forward=dict(forward),
                btotal=btotal,ftotal=ftotal,self_count=self_count,partner_year=dict(partner_year),
                partner_year_tot=partner_year_tot,dedup_removed=dedup_removed)
    save_cache('citation_stats.pkl',result)
    return result

def construct():
    patents,owners,powners=augment_ownership(); maps,dates=classification(); s=scan_citations()
    grant_audit=pd.read_csv(OUT/'grant_date_audit.csv')
    withdrawn=set(grant_audit.loc[grant_audit.withdrawn.eq(1),'patent_id'].astype(int))
    excluded=patents.loc[patents.patent_id.isin(withdrawn)].copy()
    excluded['exclusion_reason']='withdrawn_grant_replaced_by_valid_grant_for_same_application'
    excluded.to_csv(OUT/'withdrawn_grant_exclusions.csv',index=False,encoding='utf-8-sig')
    patents=patents.loc[~patents.patent_id.isin(withdrawn)].copy()
    arr,labels=maps[s['scheme']]; size=len(labels)
    target=pd.read_csv(TARGET.with_suffix('.csv'),low_memory=False)
    pairs=anchored_pairs()
    pids_by_partner=defaultdict(set)
    for pid,ps in powners.items():
        for p in ps: pids_by_partner[p].add(pid)
    partner_profiles={}; partner_audit=[]
    partner_events=defaultdict(list); partner_totals=defaultdict(list)
    for (pk,day),counts in s['partner_year'].items(): partner_events[pk].append((day,counts))
    for (pk,day),cnt in s['partner_year_tot'].items(): partner_totals[pk].append((day,cnt))
    profile_counts={}
    for r in pairs.itertuples():
        key=(r.partner_key,int(r.reference_date))
        if key not in partner_profiles:
            counts=Counter()
            for day,c in partner_events.get(r.partner_key,[]):
                if day<=r.reference_date: counts.update(c)
            total=sum(counts.values()); vector=np.zeros(size)
            if total:
                for c,n in counts.items(): vector[c]=n/total
            partner_profiles[key]=vector if total else None
            total_refs=sum(cnt for day,cnt in partner_totals.get(r.partner_key,[]) if day<=r.reference_date)
            profile_counts[key]=(total,total_refs)
        profile=partner_profiles[key]
        npre=sum(0<dates[pid]<=int(r.reference_date) for pid in pids_by_partner.get(r.partner_key,[]))
        classified_refs,total_refs=profile_counts[key]
        partner_audit.append((r.firm_id,r.partner_key,int(r.reference_year),npre,int(profile is not None),
            'usable' if profile is not None else ('ambiguous_investor_identity' if ambiguous_partner(r.partner_key)
            else ('no_classified_backward_citations' if npre else 'no_matched_pre_reference_patents')),
            int(r.reference_date),classified_refs,total_refs,classified_refs/total_refs if total_refs else np.nan))
    audit=pd.DataFrame(partner_audit,columns=['firm_id','partner_key','reference_year','pre_reference_patents','usable','status',
                        'reference_date','classified_references','total_references','classification_coverage'])
    audit.to_csv(OUT/'partner_coverage_audit.csv',index=False,encoding='utf-8-sig')
    # Fixed, pretreatment covariance, no post-VD patent contributes to scaling.
    covariance_vectors=[x for x in partner_profiles.values() if x is not None]
    for fid,g in patents.loc[patents.event_time.lt(0)].groupby('firm_id'):
        counts=Counter()
        for pid in g.patent_id:
            if dates[pid] and dates[pid]<=int(g.reference_year.iloc[0])*10000+1231: counts.update(s['backward'].get(pid,{}))
        if counts:
            v=np.zeros(size)
            for c,n in counts.items(): v[c]=n/sum(counts.values())
            covariance_vectors.append(v)
    assert len(covariance_vectors)>2, 'Insufficient pretreatment profiles for Mahalanobis covariance'
    X=np.array(covariance_vectors); cov=np.cov(X,rowvar=False)
    eigen,vec=np.linalg.eigh(cov); retain=eigen>max(eigen.max()*1e-8,1e-12)
    rank=int(retain.sum()); transform=vec[:,retain]/np.sqrt(eigen[retain])
    # Normalize by sqrt(rank): RMS standardized distance, not min-max scaling.
    transform=transform/np.sqrt(rank)
    np.savez_compressed(OUT/'distance_covariance.npz',covariance=cov,transform=transform,classes=np.array(labels))
    byfirm=defaultdict(list)
    for r in pairs.itertuples():
        v=partner_profiles[(r.partner_key,int(r.reference_date))]
        if v is not None: byfirm[r.firm_id].append((r.partner_key,v,v@transform))
    results=[]; pair_results=[]
    for r in patents.itertuples():
        pid=int(r.patent_id); b=s['backward'].get(pid,{}); f=s['forward'].get(pid,{})
        bt=s['btotal'].get(pid,0); ft=s['ftotal'].get(pid,0); bc=sum(b.values()); fc=sum(f.values())
        own=int(arr[pid]); classified=own>=0
        # Literal paper p.916: sum excludes own class; denominator is all backward citations.
        complete=(bt>0 and bc==bt and classified)
        originality=1-sum((n/bt)**2 for c,n in b.items() if c!=own) if complete else np.nan
        conventional=1-sum((n/bt)**2 for n in b.values()) if bt>0 and bc==bt else np.nan
        breadth=len(b) if bt>0 and bc==bt else np.nan
        generality=1-sum((n/ft)**2 for n in f.values()) if ft>0 and fc==ft else np.nan
        selfc=int(s['self_count'].get((r.firm_id,pid),0))
        search=[]; distances=[]
        if bc==bt:
            v=np.zeros(size)
            for c,n in b.items(): v[c]=n
            proj=(v/bt)@transform if bt else None
            for pk,pv,pproj in byfirm.get(r.firm_id,[]):
                score=float(v@pv)
                distance=float(np.linalg.norm(proj-pproj)) if bt else np.nan
                search.append(score)
                if np.isfinite(distance): distances.append(distance)
                pair_results.append((r.firm_id,pid,pk,score,distance))
        results.append((r.firm_id,pid,originality,breadth,selfc,np.mean(search) if search else np.nan,
            np.mean(distances) if distances else np.nan,generality,conventional,bt,bc,ft,fc,
            own if own>=0 else np.nan,len(byfirm.get(r.firm_id,[]))))
    cols=['firm_id','patent_id']+METRICS+['originality_all_classes','backward_citations','classified_backward_citations',
        'forward_citations','classified_forward_citations','primary_class_code','usable_partners']
    result=patents.merge(pd.DataFrame(results,columns=cols),on=['firm_id','patent_id'],validate='one_to_one')
    result['classification']=s['scheme']; result['citation_cutoff']='2024-12-31'
    result['ultimately_granted']=1
    result['primary_class']=result.primary_class_code.map(lambda c: labels[int(c)] if pd.notna(c) else '')
    result['grant_date']=result.patent_id.map(lambda p: dates[int(p)])
    assert result.grant_date.between(1,CUTOFF).all()
    result.to_csv(OUT/'ultimately_granted_patent_measures.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(pair_results,columns=['firm_id','patent_id','partner_key','search_in_partners_domains','technological_distance']).to_csv(
        OUT/'patent_partner_measures.csv',index=False,encoding='utf-8-sig')
    win=result.loc[result.event_time.between(1,3)]
    agg=win.groupby('firm_id')[METRICS].mean().add_suffix('_win3')
    agg['originality_all_classes_win3']=win.groupby('firm_id').originality_all_classes.mean()
    # Search is a citation-volume measure in the paper: sum patent contributions
    # first; log1p applied after equal weighting across the fixed partner set.
    raw_search=win.groupby('firm_id').search_in_partners_domains.sum(min_count=1)
    agg['search_in_partners_domains_win3']=np.log1p(raw_search)
    agg['partner_search_raw_win3']=raw_search
    agg['self_citations_total_win3']=win.groupby('firm_id').self_citations.sum(min_count=1)
    agg['py_granted_patents_win3']=win.groupby('firm_id').size()
    agg['py_originality_n_win3']=win.groupby('firm_id').patent_originality.count()
    agg['py_generality_n_win3']=win.groupby('firm_id').patent_generality.count()
    agg['py_distance_n_win3']=win.groupby('firm_id').technological_distance.count()
    agg['partners_total_pre']=audit.groupby('firm_id').size()
    agg['partners_usable_pre']=audit.groupby('firm_id').usable.sum()
    # Counts of partners are also retained for firms with no post patents.
    agg=agg.reindex(target.firm_id)
    agg['partners_total_pre']=target.firm_id.map(audit.groupby('firm_id').size()).to_numpy()
    agg['partners_usable_pre']=target.firm_id.map(audit.groupby('firm_id').usable.sum()).to_numpy()
    for c in ['partners_total_pre','partners_usable_pre','py_granted_patents_win3','py_originality_n_win3','py_generality_n_win3','py_distance_n_win3']:
        agg[c]=agg[c].fillna(0).astype(int)
    absent=agg.py_granted_patents_win3.eq(0)
    agg.loc[absent,'self_citations_total_win3']=0
    # Absence of a patent is not zero originality/distance/generality.
    newcols=list(agg.columns); assert all(len(c)<=32 for c in newcols)
    old_target=target.copy()
    target=target.drop(columns=[c for c in newcols if c in target]).merge(agg.reset_index(),on='firm_id',how='left',validate='one_to_one')
    assert len(target)==2820 and target.firm_id.is_unique
    for c in old_target.columns:
        if c not in newcols: pd.testing.assert_series_equal(old_target[c],target[c],check_names=False)
    # Preserve all existing DTA columns, labels, and formats; append by firm ID.
    with pd.io.stata.StataReader(TARGET.with_suffix('.dta')) as reader:
        variable_labels=reader.variable_labels(); value_labels=reader.value_labels()
    old_dta=pd.read_stata(TARGET.with_suffix('.dta'),convert_categoricals=False)
    dta=old_dta.drop(columns=[c for c in newcols if c in old_dta]).merge(agg.reset_index(),on='firm_id',how='left',validate='one_to_one')
    labels={'patent_originality_win3':'Patent originality: mean; own class excluded per paper p916',
            'bc_technological_breadth_win3':'Backward-citation technological breadth: mean distinct classes',
            'self_citations_win3':'Self-citations: mean count per granted patent in t+1..t+3',
            'search_in_partners_domains_win3':'Search in partners domains: ln(1+equal-partner weighted citations)',
            'technological_distance_win3':'Technological distance: mean RMS Mahalanobis to fixed partners',
            'patent_generality_win3':'Patent generality: mean forward-citation class diversity'}
    variable_labels.update(labels)
    for c in dta.select_dtypes(include='object'): dta[c]=dta[c].fillna('').astype(str)
    stage_csv=OUT/'table3_staging.csv'; stage_dta=OUT/'table3_staging.dta'
    target.to_csv(stage_csv,index=False,encoding='utf-8-sig')
    dta.to_stata(stage_dta,write_index=False,version=118,variable_labels=variable_labels,
                 value_labels={k:v for k,v in value_labels.items() if k in dta})
    check=pd.read_stata(stage_dta,convert_categoricals=False)
    for c in newcols: np.testing.assert_allclose(check[c],target[c],equal_nan=True)
    backup=OUT/'before_polidoro_yang'; backup.mkdir(exist_ok=True)
    for ext in ['.csv','.dta']:
        dest=backup/('table3_current_2820_cross_section_v2'+ext)
        if not dest.exists(): shutil.copy2(TARGET.with_suffix(ext),dest)
    shutil.copyfile(stage_csv,TARGET.with_suffix('.csv')); shutil.copyfile(stage_dta,TARGET.with_suffix('.dta'))
    method={
        'source':'Polidoro & Yang (2021), Organization Science 32(4), 909-939; pp915-916,920,931,935-936',
        'classification':s['scheme'],'classification_coverage':s['coverage'],
        'cutoff':'2024-12-31; available local PatentsView snapshot; NOT a 2025 update',
        'partner_definition':'All named investors in any observed funding type by first debt date in VD year, where available, otherwise reference year-end; fixed thereafter. Exact normalized assignee names or sourced parent alias only. Portfolio companies excluded.',
        'partner_baseline':'Own granted patents granted by reference date; backward citation profiles fixed at baseline. Shares are normalized across classified numeric US patent references; coverage fraction retained in partner audit.',
        'originality':'Literal p916: 1 - sum_{class != focal primary class} (citations_class / all backward patent citations)^2. Missing with zero references or incomplete classification. Conventional all-class alternative retained at patent level.',
        'breadth':'Count all distinct backward-cited primary classes; missing with zero/incompletely classified backward citations.',
        'self_citations':'Count distinct US backward-cited patents sharing the matched startup owner; not restricted to event window for cited prior patents.',
        'generality':'1 - sum(forward citing patent primary-class shares squared), through snapshot; missing with no forward citations or incomplete class mapping.',
        'search':'Patent-level sum class counts times partner pretreatment backward-class shares, equal average over usable partners; firm window ln(1+sum patent contributions).',
        'distance':'Patent backward-citation proportion vector vs each fixed partner vector. Covariance from unique partner-baseline and pre-VD startup profiles. Eigenvalue cutoff max(1e-8*max_eigenvalue,1e-12), pseudoinverse; sqrt(quadratic_form/rank). Equal partner average then patent mean. Explicit implementation choice: article does not specify exact normalization.',
        'distance_covariance_rank':rank,'distance_reference_profiles':len(X),
        'firm_window':'Ultimately granted patents filed reference_year+1..+3; patent means except log sum for partner search. Multiple grant documents are separate patent observations.',
        'partner_date_limitation':'Actual first debt date in VD year when observed. Year-end reference for controls and treated firms lacking an identified dated debt round; per-firm date_basis is saved.',
        'matching_limitation':'No-match is not proof of zero patents. Unmatched institutions retained as unusable with reason. Acquired-parent historical ownership is not inferred.',
        'adaptations':'All VC/CVC/VD partners instead of one CVC; fixed baseline instead of rolling partner weights; post-window patent means instead of cumulative lifetime; explicit covariance normalization; modern CPC if USPC coverage insufficient.',
        'rows_patent':len(result),'rows_window':len(win),'rows_cross_section':len(target),
        'withdrawn_grant_documents_excluded':len(excluded),
        'citation_universe':'US numeric utility-patent citations; foreign, nonpatent, design and reissue references excluded. Old numeric references retained in denominators even when their classification is unavailable.',
        'nonmissing_firms':{c:int(target[c+'_win3'].notna().sum()) for c in METRICS},
        'partner_status_counts':audit.status.value_counts().to_dict(),
        'preserved_existing_columns':True,'csv_dta_new_columns_equal':True}
    (OUT/'methodology_and_QA.json').write_text(json.dumps(method,indent=2,ensure_ascii=False),encoding='utf-8')
    log(json.dumps(method,indent=2,ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--stage',choices=['deals','ownership','augment','class','citations','construct'],default='construct')
    args=parser.parse_args()
    {'deals':extract_deals,'ownership':prepare_ownership,'augment':augment_ownership,'class':classification,'citations':scan_citations,'construct':construct}[args.stage]()
