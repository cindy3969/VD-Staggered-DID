"""Preserve existing measures, add concise analysis aliases and own-portfolio DVs.

No refresh of the 2024 citation cutoff. Primary CPC3, fixed pre-reference
granted portfolio, not an all-CPC or novel-combination measure.
"""
from pathlib import Path
from collections import Counter, defaultdict
import json, pickle, shutil
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT/'outputs/psm_final_2820_package'
PY = ROOT/'outputs/innovation_measures_2820/polidoro_yang'
OUT = ROOT/'outputs/innovation_measures_2820/trajectory'
OUT.mkdir(exist_ok=True)
STEM = PKG/'table3_current_2820_cross_section_v2'
# Preserve long names for backward compatibility with earlier builders/do-files.
ALIASES = {
 'nocite_win3': ('no_citation_share_win3','No-future-citation share; granted apps filed t+1..t+3; cutoff 2024'),
 'breakthrough_win3': ('breakthrough_patent_share_win3','Top-5% citation share within filing year x CPC3; cutoff 2024'),
 'desc_words_win3': ('description_words_mean_win3','Mean description word count; granted applications filed t+1..t+3'),
 'fog_win3': ('gunning_fog_mean_win3','Mean Gunning Fog years; granted apps t+1..t+3; higher=less readable'),
 'ari_win3': ('ari_mean_win3','Mean automated readability grade; t+1..t+3; higher=less readable'),
 'neg_flesch_win3': ('neg_flesch_mean_win3','Mean minus Flesch reading ease; t+1..t+3; higher=less readable'),
 'figures_win3': ('figures_mean_win3','Mean figures per granted application filed t+1..t+3'),
 'sheets_win3': ('sheets_mean_win3','Mean drawing sheets per granted application filed t+1..t+3'),
 'claims_win3': ('claims_mean_win3','Mean claims per granted application filed t+1..t+3'),
 'ind_claims_win3': ('indep_claims_mean_win3','Mean independent claims per granted application filed t+1..t+3'),
 'dep_claims_win3': ('dep_claims_mean_win3','Mean dependent claims per granted application filed t+1..t+3'),
 'originality_win3': ('patent_originality_win3','Mean originality, own CPC3 excluded per PY p916; t+1..t+3'),
 'cite_breadth_win3': ('bc_technological_breadth_win3','Mean distinct backward-cited primary CPC3 classes; t+1..t+3'),
 'selfcite_win3': ('self_citations_win3','Mean self-citation count per granted patent; t+1..t+3'),
 'partner_search_win3': ('search_in_partners_domains_win3','ln(1+sum partner-weighted backward citations); fixed VC/CVC/VD set'),
 'partner_dist_win3': ('technological_distance_win3','Mean RMS Mahalanobis distance to investor portfolios; t+1..t+3'),
 'generality_win3': ('patent_generality_win3','Mean forward-citing CPC3 diversity; t+1..t+3; citation cutoff 2024'),
 'cite_diversity_win3': ('originality_all_classes_win3','Mean 1-HHI of all backward-cited CPC3 shares; t+1..t+3'),
}
LABELS = {
 'win3_observed':'1 if reference year+3 <= 2024 snapshot; not equal grant follow-up age',
 'grant_rate_win3':'Granted / all applications filed t+1..t+3; observed cutoff 2024',
 'base_patents':'Matched own patents granted before reference year; all observed history',
 'base_cpc':'Distinct primary CPC3 in own pre-reference granted portfolio',
 'base_cpc_cov':'Share of pre-reference granted patents with primary CPC3 mapped',
 'newpat_win3':'Count post patents in CPC3 absent from own pre-reference portfolio',
 'oldpat_win3':'Count post patents in CPC3 present in own pre-reference portfolio',
 'newshare_win3':'New-domain / all classified post patents; baseline required; t+1..t+3',
 'newcpc_win3':'Distinct new primary CPC3 entered in t+1..t+3; baseline required',
 'own_dist_win3':'Mean 1-cosine(primary CPC3, own pre-reference distribution); t+1..t+3',
 'selfshare_win3':'Self / all backward citations pooled over t+1..t+3 patents',
 'post_cpc_cov':'Share of t+1..t+3 granted patents with primary CPC3 mapped',
}

def main():
    csv=pd.read_csv(STEM.with_suffix('.csv'),low_memory=False)
    dta=pd.read_stata(STEM.with_suffix('.dta'),convert_categoricals=False)
    with pd.io.stata.StataReader(STEM.with_suffix('.dta')) as r:
        vl=r.variable_labels(); values=r.value_labels()
    p=pd.read_csv(PY/'ultimately_granted_patent_measures.csv')
    with open(PY/'ownership_augmented.pkl','rb') as f: _,owners,_=pickle.load(f)
    with open(PY/'classification.pkl','rb') as f: maps,dates=pickle.load(f)
    classes,classlabels=maps['CPC3']
    years=csv.set_index('firm_id').VDyear.to_dict()
    withdrawn=set(pd.read_csv(PY/'withdrawn_grant_exclusions.csv').patent_id)
    counts=defaultdict(Counter); nbase=Counter()
    # Prior-year end removes all treatment-year ambiguity. No future grants
    # enter the fixed baseline, even if their applications predate treatment.
    for pid,firms in owners.items():
        if pid in withdrawn or pid>=len(dates) or dates[pid]<=0: continue
        for fid in firms:
            if fid in years and dates[pid]<int(years[fid])*10000+101:
                nbase[fid]+=1
                if classes[pid]>=0: counts[fid][int(classes[pid])]+=1
    out=[]
    for r in p.itertuples():
        b=counts[r.firm_id]; complete=nbase[r.firm_id]>0 and sum(b.values())==nbase[r.firm_id]
        c=classes[r.patent_id]
        valid=complete and c>=0
        new=float(c not in b) if valid else np.nan
        distance=1-b.get(int(c),0)/np.sqrt(sum(x*x for x in b.values())) if valid else np.nan
        out.append((new,distance))
    p[['new_domain','own_distance']]=out
    p['baseline_end']=(p.reference_year.astype(int)-1)*10000+1231
    w=p[p.event_time.between(1,3)]
    rows=[]
    for fid in csv.firm_id:
        z=w[w.firm_id.eq(fid)]; b=counts[fid]; nb=nbase[fid]
        complete=nb>0 and sum(b.values())==nb
        post_complete=z.primary_class.notna().all()
        observed=years[fid]+3<=2024
        usable=complete and post_complete and observed
        new=z.new_domain.sum() if usable else np.nan
        old=len(z)-new if usable else np.nan
        nc=z.loc[z.new_domain.eq(1),'primary_class'].nunique() if usable else np.nan
        bt=z.backward_citations.sum()
        rows.append(dict(firm_id=fid,win3_observed=int(observed),base_patents=nb,base_cpc=len(b),
            base_cpc_cov=sum(b.values())/nb if nb else np.nan,
            newpat_win3=new,oldpat_win3=old,newshare_win3=new/len(z) if usable and len(z) else np.nan,
            newcpc_win3=nc,own_dist_win3=z.own_distance.mean() if usable and len(z) else np.nan,
            selfshare_win3=z.self_citations.sum()/bt if bt and observed else np.nan,
            post_cpc_cov=z.primary_class.notna().mean() if len(z) else np.nan))
    extra=pd.DataFrame(rows).set_index('firm_id')
    assert extra.index.is_unique
    valid=extra.newpat_win3.notna()
    np.testing.assert_allclose((extra.newpat_win3+extra.oldpat_win3)[valid],
        extra.index.to_series().map(w.groupby('firm_id').size()).fillna(0)[valid])
    for c in ['newshare_win3','own_dist_win3','selfshare_win3']:
        assert extra[c].dropna().between(-1e-12,1+1e-12).all()
    backup=PKG/'backups/before_innovation_analysis_20261019'; backup.mkdir(exist_ok=True)
    for suffix in ['.csv','.dta']:
        dest=backup/(STEM.name+suffix)
        if not dest.exists(): shutil.copy2(STEM.with_suffix(suffix),dest)
    do=PKG/'RUN_TABLE3_PATENT_APPLICATION_WIN3.do'
    if not (backup/do.name).exists(): shutil.copy2(do,backup/do.name)
    dictionary=[]
    for frame in [csv,dta]:
        for alias,(source,label) in ALIASES.items(): frame[alias]=frame[source]
        for c in extra: frame[c]=frame.firm_id.map(extra[c])
    for alias,(source,label) in ALIASES.items():
        vl[alias]=label
        dictionary.append(dict(variable=alias,source=source,label=label,nonmissing=int(csv[alias].notna().sum())))
    for c,label in LABELS.items():
        vl[c]=label
        dictionary.append(dict(variable=c,source='own primary CPC3 baseline' if c!='grant_rate_win3' else 'existing measure',label=label,nonmissing=int(csv[c].notna().sum())))
    assert all(len(v)<=80 for v in vl.values())
    assert len(csv)==2820 and csv.firm_id.is_unique
    stagecsv=OUT/'staging.csv'; stagedta=OUT/'staging.dta'
    # Retain the literal representation of every existing CSV field, avoiding
    # a floating-point parse/write round trip for unrelated data.
    csv_text=pd.read_csv(STEM.with_suffix('.csv'),dtype=str,keep_default_na=False)
    for c in list(ALIASES)+list(extra): csv_text[c]=csv[c]
    csv_text.to_csv(stagecsv,index=False,encoding='utf-8-sig')
    dta.to_stata(stagedta,write_index=False,version=118,variable_labels=vl,value_labels=values)
    chk=pd.read_stata(stagedta,convert_categoricals=False)
    old=pd.read_stata(backup/(STEM.name+'.dta'),convert_categoricals=False)
    pd.testing.assert_frame_equal(old,chk[old.columns],check_dtype=False,check_exact=True)
    oldcsv=pd.read_csv(backup/(STEM.name+'.csv'),low_memory=False)
    pd.testing.assert_frame_equal(oldcsv,pd.read_csv(stagecsv)[oldcsv.columns],check_dtype=False,check_exact=True)
    for c in list(ALIASES)+list(extra): np.testing.assert_allclose(csv[c],chk[c],equal_nan=True)
    shutil.copyfile(stagecsv,STEM.with_suffix('.csv')); shutil.copyfile(stagedta,STEM.with_suffix('.dta'))
    p.to_csv(OUT/'patent_trajectory.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(dictionary).to_csv(OUT/'innovation_dictionary.csv',index=False,encoding='utf-8-sig')
    audit={'firms':len(csv),'patents':len(p),'window_patents':len(w),'window':'filing years reference+1..+3',
        'baseline':'All matched own patents granted before reference year; fixed primary CPC3. Empty/incomplete baseline => missing.',
        'zero_rule':'Counts zero for baseline-eligible firms with no post patents; composition/distance remain missing.',
        'limitations':['Static assignee linkage, not historical ownership reconstruction.','Primary CPC3 only; not all classifications or recombination.','Citation cutoff remains 2024; no 2025 refresh.','Granted-patent selection and post-patenting selection limit causal interpretation.'],
        'vd_year_range':[int(csv.VDyear.min()),int(csv.VDyear.max())],
        'nonmissing':{c:int(csv[c].notna().sum()) for c in list(ALIASES)+list(extra)}}
    (OUT/'construction_QA.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    print(json.dumps(audit,indent=2))

if __name__=='__main__': main()
