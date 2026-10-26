"""Recover original Table 8 without treating last-deal year as employee date."""
from pathlib import Path
from datetime import datetime
import shutil,json
import pandas as pd
import numpy as np
B=Path(__file__).resolve().parents[1]
P=B/'outputs/psm_final_2820_package'; O=P/'postvd_size_research'
source=B/'260122 winsorization_stage4.dta'
d=pd.read_stata(source,convert_categoricals=False)
q=d[d.private.eq(1)&d.lastdeal2vd1.between(1,3)].copy()
assert len(q)==611 and d.OrganizationName.is_unique
q.to_stata(O/'recovered_table8_original_611.dta',write_index=False,version=118)
q.to_csv(O/'recovered_table8_original_611.csv',index=False)
rows=[]
for model in range(1,6):
    x=pd.DataFrame({'constant':1.,'VD':q.VD},index=q.index)
    if model>1:
        for c in ['patentdummybyfiling','earlystage','ln_MoneyRaised_VD','NumofFundingRounds_VD']: x[c]=q[c]
        if model in [3,5]: x['VD_x_patent']=q.VD*q.patentdummybyfiling
        if model in [4,5]: x['VD_x_earlystage']=q.VD*q.earlystage
    for c,base in ([('lastdeal2vd1',1)]+([('Founding_Year',q.Founding_Year.min()),('Region2',4),('Industry2',3)] if model>1 else [])):
        for v in sorted(q[c].dropna().unique()):
            if v!=base: x[f'{c}_{v}']=q[c].eq(v).astype(float)
    valid=x.notna().all(axis=1)&q.emp2025_2.notna()
    a=x[valid].to_numpy(float); y=q.loc[valid,'emp2025_2'].to_numpy(float)
    b=np.linalg.lstsq(a,y,rcond=None)[0]; e=y-a@b; rank=np.linalg.matrix_rank(a)
    bread=np.linalg.pinv(a.T@a); meat=a.T@((e**2)[:,None]*a)
    se=np.sqrt(np.maximum(0,np.diag(bread@meat@bread)*len(y)/(len(y)-rank)))
    for i,c in enumerate(x): rows.append(dict(model=model,term=c,coefficient=b[i],robust_se=se[i],N=len(y),R2=1-e@e/((y-y.mean())@(y-y.mean()))))
audit=pd.DataFrame(rows); audit.to_csv(O/'table8_recovered_coefficients.csv',index=False)
print(audit[audit.term.isin(['constant','VD'])].to_string(index=False))
f=P/'table3_current_2820_cross_section_v2.dta'
with pd.io.stata.StataReader(f) as r:
    labels=r.variable_labels(); vl=r.value_labels(); dl=r.data_label
    m=r.read(convert_categoricals=False)
    vlabels={v:vl[l] for v,l in zip(r._varlist,r._lbllist) if l in vl}
original=m.copy(); lookup=d.set_index('OrganizationName')
mapping={'employees_legacy':'emp2025_2','emp_legacy_lastdeal':'lastdeal','emp_legacy_t':'lastdeal2vd1','emp_legacy_VDyear':'VDyear'}
for new,old in mapping.items(): m[new]=m.OrganizationName.map(lookup[old])
m['emp_legacy_table8']=m.OrganizationName.isin(q.OrganizationName).astype('int8')
labels.update({'employees_legacy':'Original emp2025_2; employee observation year UNVERIFIED',
 'emp_legacy_lastdeal':'Legacy last deal year; NOT verified employee observation year',
 'emp_legacy_t':'Original Table8 lastdeal2vd1; NOT verified employee timing',
 'emp_legacy_VDyear':'Reference VDyear in original Table8 source',
 'emp_legacy_table8':'Company name in original 611-firm Table8 sample'})
added=list(mapping)+['emp_legacy_table8']
for c in original:
    if c not in added: pd.testing.assert_series_equal(original[c],m[c])
backup=P/'backups'/('before_legacy_recovery_'+datetime.now().strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True)
for path in [f,f.with_suffix('.csv')]: shutil.copy2(path,backup/path.name)
stage=O/'legacy_validated.dta'
m.to_stata(stage,write_index=False,version=118,variable_labels=labels,value_labels=vlabels,data_label=dl)
pd.testing.assert_frame_equal(m,pd.read_stata(stage,convert_categoricals=False),check_dtype=False)
c=pd.read_csv(f.with_suffix('.csv')).drop(columns=added,errors='ignore')
c=c.merge(m[['firm_id']+added],on='firm_id',validate='one_to_one',sort=False)
c.to_csv(f.with_suffix('.csv'),index=False);shutil.copy2(stage,f)
cross=m[['firm_id','OrganizationName','VDyear']+added].copy()
cross.to_csv(O/'legacy_employee_crosswalk.csv',index=False)
summary={'matched_legacy_employee_firms':int(m.employees_legacy.notna().sum()),'original_table8_N':611,'original_table8_current_cohort_overlap':int(m.emp_legacy_table8.sum()),'lastdeal_difference_equals_t':int((d.lastdeal-d.VDyear).eq(d.lastdeal2vd1).sum()),'legacy_total':len(d),'source':str(source),'employee_date_verified':False,'backup':str(backup)}
(O/'legacy_recovery_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
print(json.dumps(summary,indent=2))
commands=['clear all',f'use "{(O/"recovered_table8_original_611.dta").as_posix()}", clear','* Original sample and covariates; employee measurement date is unverified.']
rhs=['VD','VD patentdummybyfiling earlystage','i.VD##ib0.patentdummybyfiling earlystage','patentdummybyfiling i.VD##ib0.earlystage','i.VD##ib0.patentdummybyfiling i.VD##ib0.earlystage']
for i,s in enumerate(rhs):
    controls=' i.lastdeal2vd1' if i==0 else ' ln_MoneyRaised_VD NumofFundingRounds_VD i.lastdeal2vd1 i.Founding_Year ib4.Region2 ib3.Industry2'
    commands += [f'regress emp2025_2 {s}{controls}, vce(robust)',f'estimates store table8_{i+1}']
(O/'REPLICATE_ORIGINAL_TABLE8.do').write_text('\n'.join(commands)+'\n',encoding='utf8')
