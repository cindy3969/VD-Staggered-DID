from pathlib import Path
import pandas as pd,numpy as np,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/table67_merge_audit'
OUT.mkdir(exist_ok=True)
OLD=Path('C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms/260122 winsorization.dta')
NEW=ROOT/'outputs/psm_final_2820_package/table3_original_2820_cross_section_v2.dta'
a=pd.read_stata(OLD,convert_categoricals=False).set_index('firm_id').sort_index()
b=pd.read_stata(NEW,convert_categoricals=False).set_index('firm_id').sort_index()
assert a.index.is_unique and b.index.is_unique and a.index.equals(b.index)
changed={}
for c in a:
    if c not in b:changed[c]='absent';continue
    same=a[c].eq(b[c])|(a[c].isna()&b[c].isna())
    if not same.all():changed[c]=int((~same).sum())
report={'firms':len(a),'old_columns_including_id':len(a.columns)+1,'changed_legacy_columns':changed,
        'VD_counts':b.VD.value_counts().to_dict(),
        'old_relevant_variables':[c for c in a if any(s in c.lower() for s in ['raised','exit','acq','public','age','early','ipo','status','defunct'])]}
report['annual_financing']={}
for t in [1,2,3]:
    old=f'ln_moneyraised_y{t}'
    raw=f'{"equityraised" if t==3 else "moneyraised"}_t{t}'
    if old in a:
        x=a[old];y=np.log1p(b[raw]);both=x.notna()&y.notna()
        report['annual_financing'][str(t)]={'old':old,'current':'ln(1+'+raw+')',
           'old_nonmissing':int(x.notna().sum()),'current_nonmissing':int(y.notna().sum()),
           'both_nonmissing':int(both.sum()),'different_values_when_both':int((~np.isclose(x[both],y[both])).sum()),
           'old_only':int((x.notna()&y.isna()).sum()),'current_only':int((x.isna()&y.notna()).sum())}
report['legacy_events']={c:{'nonmissing':int(a[c].notna().sum()),'ones':int(a[c].eq(1).sum())}
    for c in ['VDage3','acq3','public3','badexit3'] if c in a}
report['status_counts']=b.status.value_counts().to_dict()
report['old_exit_counts']=a.exittype2.value_counts(dropna=False).to_dict()
(OUT/'comparison.json').write_text(json.dumps(report,indent=2,ensure_ascii=True))
print(json.dumps(report,indent=2,ensure_ascii=True))
# Independently run identical legacy specifications on both files, then current Table 6.
code=['version 19','clear all','set more off',f'log using "{OUT.as_posix()}/audit.log", text replace',
      f'postfile audit str12 source str16 model str60 term double b se p N failures using "{OUT.as_posix()}/estimates.dta", replace',
      '''program define record_model
syntax, Source(string) Model(string)
tempname B V
matrix `B'=e(b)
matrix `V'=e(V)
local names : colnames `B'
forvalues j=1/`=colsof(`B')' {
local term : word `j' of `names'
local se=sqrt(`V'[`j',`j'])
local prob=.
if `se'>0 & !missing(`se') {
if !missing(e(df_r)) local prob=2*ttail(e(df_r),abs(`B'[1,`j']/`se'))
else local prob=2*normal(-abs(`B'[1,`j']/`se'))
}
post audit ("`source'") ("`model'") ("`term'") (`B'[1,`j']) (`se') (`prob') (e(N)) (e(N_fail))
}
end''']
for src,path in [('legacy',OLD),('current',NEW)]:
    code += [f'use "{path.as_posix()}", clear',
             'capture drop audit_prior','gen audit_prior=patentdummybyfiling']
    for t in [1,2,3]:
        code += [f'reghdfe ln_moneyraised_y{t} VD i.audit_prior i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)',
                 f'record_model, source({src}) model(T6_legacy_{t})']
    for event in ['acq3','public3','badexit3']:
        code += [f'stset VDage3, failure({event}==1) id(firm_id)',
                 'stcox VD i.Region2 i.Industry2 i.Foundingyear, nohr',
                 f'record_model, source({src}) model({event}_base)',
                 'stcox VD audit_prior earlystage ln_MoneyRaised_VD NumofFundingRounds_VD i.Region2 i.Industry2 i.Foundingyear, nohr',
                 f'record_model, source({src}) model({event}_ctrl)']
    if src=='current':
        for t in [1,2,3]:
            raw=f'{"equityraised" if t==3 else "moneyraised"}_t{t}'
            code += ['capture drop audit_dv',f'gen audit_dv=ln(1+{raw})',
             'reghdfe audit_dv VD i.audit_prior i.earlystage ln_MoneyRaised_VD NumofFundingRounds_VD, absorb(Region2 Industry2 Foundingyear) vce(robust)',
             f'record_model, source(current) model(T6_new_{t})']
code+=['postclose audit','display "AUDIT_COMPLETE"','log close']
(OUT/'audit.do').write_text('\n'.join(code)+'\n',encoding='utf-8')
