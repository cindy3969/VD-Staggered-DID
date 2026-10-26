from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'outputs/psm_final_2820_package'
OUT = ROOT / 'outputs/reference_timing_audit_2820'
OUT.mkdir(exist_ok=True)
d = pd.read_stata(P / 'table3_current_2820_cross_section_v2.dta', convert_categoricals=False)
m = pd.read_stata(P / 'psm_stata_matched_2820.dta', convert_categoricals=False)
d = d.merge(m[['OrganizationName','TimeToFirst_VC','TimeToFirst_VD','TimeBetween_VCVD','VDYear','Founding_Year']], on='OrganizationName', validate='one_to_one')
d['reference_age'] = d.VDyear-d.Foundingyear
d['first_vc_year_implied'] = d.Foundingyear+d.TimeToFirst_VC
d['reference_since_first_vc'] = d.VDyear-d.first_vc_year_implied
lines = [f'N={len(d)}, unique firms={d.firm_id.nunique()}',
         f'Cross-section vs matching reference-year discrepancies: {(d.VDyear!=d.VDYear).sum()}',
         f'Cross-section vs matching founding-year discrepancies: {(d.Foundingyear!=d.Founding_Year).sum()}',
         'First VC year is IMPLIED by Foundingyear + stored TimeToFirst_VC; raw deal dates not independently verified.']
for group, x in d.groupby('VD'):
    lines += [f'\nVD={group}, N={len(x)}',
              f'Age !=5: {x.reference_age.ne(5).sum()}',
              f'Reference before implied first VC: {x.reference_since_first_vc.lt(0).sum()}']
    cols=['Foundingyear','VDyear','reference_age','TimeToFirst_VC','reference_since_first_vc','earlystage','NumofFundingRounds_VD','ln_MoneyRaised_VD']
    lines += [x[cols].describe(percentiles=[.05,.1,.25,.5,.75,.9,.95]).to_string()]
    for col in ['VDyear','reference_age','reference_since_first_vc']:
        freq=x[col].value_counts(dropna=False).sort_index().rename('N').to_frame()
        freq['percent']=freq.N/len(x)*100
        lines += [f'\nFull distribution: {col}',freq.to_string()]
t=d[d.VD.eq(1)]
lines += [f'\nTreated age vs stored TimeToFirst_VD discrepancies: {t.reference_age.ne(t.TimeToFirst_VD).sum()}',
          f'Treated VC-VD gap vs stored TimeBetween_VCVD discrepancies: {t.reference_since_first_vc.ne(t.TimeBetween_VCVD).sum()}',
          f'Treated <5 / =5 / >5: {t.reference_age.lt(5).sum()} / {t.reference_age.eq(5).sum()} / {t.reference_age.gt(5).sum()}',
          '\nStandardized mean differences (treated-control, pooled group variance):']
for col in ['VDyear','reference_age','reference_since_first_vc','earlystage','NumofFundingRounds_VD','ln_MoneyRaised_VD']:
    a=d.loc[d.VD.eq(1),col]; b=d.loc[d.VD.eq(0),col]
    smd=(a.mean()-b.mean())/((a.var()+b.var())/2)**.5
    lines.append(f'{col}: {smd:.4f}')
result='\n'.join(lines)
(OUT/'timing_audit.txt').write_text(result,encoding='utf-8')
d[['firm_id','OrganizationName','VD','Foundingyear','VDyear','reference_age','TimeToFirst_VC','first_vc_year_implied','reference_since_first_vc']].to_json(OUT/'firm_timing.json',orient='records',indent=2)
print(result)
