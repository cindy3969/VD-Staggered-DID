"""Append dated patent/stage states to the existing panel only.
Patent = application filed by cutoff and eventually granted in observed source.
Stage = latest equity-stage-bearing round; ambiguous equity stages stay missing.
No original column is overwritten. End-year states accompany prior-year states
so that C&S base-period selection need not double-lag the controls.
"""
from pathlib import Path
import re
import numpy as np
import pandas as pd
import zipfile
import xml.etree.ElementTree as ET

root=Path(r'C:/Users/user/Documents/VD')
path=root/'outputs/csdid_all_applications_corrected/firm_year_all_applications_and_truncation_specs.dta'
with pd.read_stata(path,iterator=True,convert_categoricals=False) as r:
    labels=r.variable_labels()
    p=r.read()
original=p.copy()
def key(x): return str(x).strip().casefold()
roster=p[['full_firm_id','organization_name']].drop_duplicates()
roster['key']=roster.organization_name.map(key)
ambiguous=roster['key'].duplicated(keep=False)
print('Ambiguous firm-name keys excluded from stage linkage:',roster.loc[ambiguous].to_string(index=False))
roster=roster.loc[~ambiguous]
source=r'C:/Users/user/OneDrive/바탕 화면/2010 2015 Crunchbase deals merged_v4.xlsx'
# Stream only four needed columns; avoid workbook-wide style/formula parsing.
ns='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
with zipfile.ZipFile(source) as z:
    strings=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        for _,e in ET.iterparse(z.open('xl/sharedStrings.xml'),events=['end']):
            if e.tag==ns+'si':
                strings.append(''.join(t.text or '' for t in e.iter(ns+'t'))); e.clear()
    rows=[]
    for _,e in ET.iterparse(z.open('xl/worksheets/sheet1.xml'),events=['end']):
        if e.tag!=ns+'row': continue
        if int(e.attrib.get('r','0'))<=2: e.clear(); continue
        vals={}
        for c in e.findall(ns+'c'):
            col=re.sub(r'\d','',c.attrib['r'])
            if col not in ['D','H','J','K']: continue
            v=c.find(ns+'v'); value=v.text if v is not None else ''
            if c.attrib.get('t')=='s' and value: value=strings[int(value)]
            elif c.attrib.get('t')=='inlineStr': value=''.join(t.text or '' for t in c.iter(ns+'t'))
            vals[col]=value
        if vals.get('D'): rows.append([vals.get(c,'') for c in ['D','H','J','K']])
        e.clear()
d=pd.DataFrame(rows,columns=['Organization Name','Announced Date','Funding Stage','Funding Type'])
serial=pd.to_numeric(d['Announced Date'],errors='coerce')
d['Announced Date']=pd.to_datetime(serial,unit='D',origin='1899-12-30',errors='coerce').where(serial.notna(),pd.to_datetime(d['Announced Date'],errors='coerce'))
print('Read deal rows:',len(d),flush=True)
d['key']=d['Organization Name'].map(key)
d=d.merge(roster[['full_firm_id','key']],on='key',validate='many_to_one')
d['date']=pd.to_datetime(d['Announced Date'],errors='coerce')
d['type']=d['Funding Type'].fillna('').astype(str).str.lower().str.strip()
d['stage']=d['Funding Stage'].fillna('').astype(str).str.lower().str.strip()
def classify(row):
    t,s=row['type'],row['stage']
    if re.match(r'^series a(?:\b|\d)',t) or t in ['seed','pre-seed','angel']: return 1.
    if re.match(r'^series [b-z](?:\b|\d)',t): return 0.
    if t in ['private equity','post-ipo equity','post-ipo secondary']: return 0.
    if s in ['seed','early stage venture']: return 1.
    if s in ['late stage venture','private equity','post-ipo equity']: return 0.
    return np.nan
# Financing types that describe equity stage (including ambiguous equity rounds).
equity=d['type'].str.contains(r'^series |seed|angel|venture|private equity|equity crowdfunding|corporate round|funding round|secondary|post-ipo equity',regex=True)
equity |= d['stage'].isin(['seed','early stage venture','late stage venture','venture - series unknown','private equity','post-ipo equity'])
d=d[equity].copy()
d['early_value']=d.apply(classify,axis=1)
bad_date=set(d.loc[d.date.isna(),'full_firm_id'])
matched=set(d.full_firm_id)
d=d[d.date.notna()].sort_values(['full_firm_id','date'])
groups={}
for (fid,date),g in d.groupby(['full_firm_id','date']):
    v=g.early_value
    value=float(v.iloc[0]) if v.notna().all() and v.nunique()==1 else np.nan
    groups.setdefault(fid,[]).append((date.year,value,' | '.join(sorted(set(g['type'])))))
apps=pd.read_csv(root/'outputs/csdid_union_corrected_3yr/application_level_union_corrected_visible_mismatches.csv',low_memory=False)
apps['filing_year']=pd.to_numeric(apps.filing_year,errors='coerce')
apps['ultimately_granted']=pd.to_numeric(apps.ultimately_granted,errors='coerce')
first=apps[apps.ultimately_granted.eq(1)].groupby('full_firm_id').filing_year.min()
new={c:[] for c in ['priorpatent_preyear','priorpatent_endyear','earlystage_preyear','earlystage_endyear','stage_preyear_text','stage_endyear_text']}
for row in p.itertuples(index=False):
    fid,y=row.full_firm_id,int(row.year)
    fy=first.get(fid,np.inf)
    new['priorpatent_preyear'].append(float(fy<y))
    new['priorpatent_endyear'].append(float(fy<=y))
    g=groups.get(fid,[])
    for cutoff,suffix in [(y,'preyear'),(y+1,'endyear')]:
        hist=[r for r in g if r[0]<cutoff]
        val=np.nan; label='No prior equity-stage record'
        if hist:
            _,val,label=hist[-1]
        if fid in bad_date: val=np.nan; label='Undated equity round: ordering unresolved'
        new['earlystage_'+suffix].append(val)
        new['stage_'+suffix+'_text'].append(label)
for c,v in new.items(): p[c]=v
atg=p[p.G.gt(0)&p.year.eq(p.G)].set_index('full_firm_id')
p['priorpatent_Gminus1']=p.full_firm_id.map(atg.priorpatent_preyear)
p['earlystage_Gminus1']=p.full_firm_id.map(atg.earlystage_preyear)
labels.update({
 'priorpatent_preyear':'Any observed ultimately-granted application filed before Jan 1 of year',
 'priorpatent_endyear':'Any observed ultimately-granted application filed by year end',
 'earlystage_preyear':'Latest equity stage before Jan 1: early=1, late=0, unknown=missing',
 'earlystage_endyear':'Latest equity stage at year end: early=1, late=0, unknown=missing',
 'priorpatent_Gminus1':'Treated subgroup: patent filing history through G-1; controls missing',
 'earlystage_Gminus1':'Treated subgroup: latest equity stage through G-1; controls missing'})
for c in original:
    assert p[c].equals(original[c]), c
assert len(p)==88547 and not p.duplicated(['full_firm_id','year']).any()
p.to_stata(path,write_index=False,version=118,variable_labels=labels)
check=pd.read_stata(path,convert_categoricals=False)
assert len(check)==len(original)
print('Updated existing DTA; original columns unchanged; rows:',len(p))
print(p.assign(treated=p.G.gt(0)).groupby('treated')[['priorpatent_preyear','earlystage_preyear','earlystage_endyear']].agg(['size','count']).to_string())
print('Treated G-1 stage counts:',atg.earlystage_preyear.value_counts(dropna=False).to_dict())
print('Treated G-1 patent counts:',atg.priorpatent_preyear.value_counts(dropna=False).to_dict())
