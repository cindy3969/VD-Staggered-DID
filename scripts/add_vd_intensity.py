from pathlib import Path
import pandas as pd, numpy as np, json, shutil
from datetime import datetime
ROOT=Path(r'C:/Users/user/Documents/VD')
TARGET=ROOT/'outputs/csdid_ultimately_granted_primary/csdid_ultimately_granted_full7316_controls.dta'
OUT=ROOT/'outputs/vd_intensity';OUT.mkdir(exist_ok=True)
SOURCE=Path(r'C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms/2010 2015 Crunchbase deals merged_v4.xlsx')
x=pd.read_excel(SOURCE,header=1)
x['Organization Name']=x['Organization Name'].astype(str)
x['amount']=pd.to_numeric(x['Money Raised Currency (in USD)'],errors='coerce')
x['date']=pd.to_datetime(x['Announced Date'],errors='coerce')
t=x['Funding Type'].fillna('').str.strip()
x['equity']=t.isin(['Seed','Pre-Seed','Angel','Venture - Series Unknown','Private Equity','Corporate Round','Equity Crowdfunding','Post-IPO Equity'])|t.str.match(r'^Series [A-I](?:\d+)?$')
# Re-runs start from the preserved original, avoiding duplicate added columns.
backups=sorted(OUT.glob('original_before_intensity_*.dta'))
BASE=backups[0] if backups else TARGET
with pd.io.stata.StataReader(BASE,convert_categoricals=False) as r:
 old=r.read(); labels=r.variable_labels(); vl=r.value_labels(); data_label=r.data_label
assert old.full_firm_id.is_unique
assert set(old.organization_name)<=set(x['Organization Name'])
assert not vl, 'Preserve value labels before proceeding'
def complete(a):
 return float(a.sum()) if a.notna().all() else np.nan
def log(a): return np.log(a) if a>0 else np.nan
def log1(a): return np.log1p(a) if pd.notna(a) and a>=0 else np.nan
rows=[]; audit=[]
groups=dict(tuple(x.groupby('Organization Name',sort=False)))
for f in old.itertuples():
 z=groups[f.organization_name].sort_values(['date','deal no'])
 r={'full_firm_id':f.full_firm_id}
 if not f.vd_backed:
  rows.append(r);continue
 first=z[z['First VD'].eq(1)]
 assert len(first)==1,(f.organization_name,len(first))
 a=first.iloc[0]; date=a['date']; amount=a.amount
 assert pd.notna(date)
 assert date.year==f.first_vd_year,(f.organization_name,date,f.first_vd_year)
 debt=z[z['Funding Type'].eq('Debt Financing')]
 assert not debt['date'].isna().any()
 earlier=debt[debt.date.lt(date)]
 debt=debt[debt.date.ge(date)]
 assert not debt.duplicated('deal no').any()
 sub=debt[debt['deal no'].ne(a['deal no'])]
 prior=z[z.equity & z.date.lt(date)]
 same=z[z.equity & z.date.eq(date)]
 prev=prior[prior.date.eq(prior.date.max())]
 # Latest prior equity date must identify a unique round; otherwise leave missing.
 prevamt=prev.amount.iloc[0] if len(prev)==1 else np.nan
 pre=complete(prior.amount); subsum=complete(sub.amount); total=complete(debt.amount)
 cap=pre+amount
 r.update(vd_initial_usd=amount,ln_vd_initial=log(amount),ln1p_vd_initial=log1(amount),
  vd_pre_equity_usd=pre,vd_prev_equity_usd=prevamt,
  vd_to_pre_equity=amount/pre if pre>0 else np.nan,
  vd_to_prev_equity=amount/prevamt if prevamt>0 else np.nan,
  vd_share_total_capital=amount/cap if cap>0 else np.nan,
  vd_subseq_rounds=len(sub),vd_subseq_usd=subsum,ln_vd_subseq=log(subsum),ln1p_vd_subseq=log1(subsum),
  vd_cumulative_usd=total,ln_vd_cumulative=log(total),ln1p_vd_cumulative=log1(total),
  vd_initial_missing=int(pd.isna(amount)),vd_earlier_debt_rounds=len(earlier),vd_pre_equity_rounds=len(prior),
  vd_pre_equity_missing_n=int(prior.amount.isna().sum()),vd_prev_equity_ties_n=len(prev),
  vd_subseq_missing_n=int(sub.amount.isna().sum()),vd_total_missing_n=int(debt.amount.isna().sum()),
  vd_subseq_known_usd=float(sub.amount.sum()),vd_cumulative_known_usd=float(debt.amount.sum()),
  vd_same_day_equity_usd=complete(same.amount),vd_same_day_equity_n=len(same),
  vd_first_date=date.strftime('%Y-%m-%d'),vd_last_source_date=z.date.max().strftime('%Y-%m-%d'))
 rows.append(r)
 for _,b in z.iterrows():
  audit.append({'full_firm_id':f.full_firm_id,'organization_name':f.organization_name,'deal_no':b['deal no'],'date':b.date,'funding_type':b['Funding Type'],'amount_usd':b.amount,'initial_vd':int(b.name==a.name),'subsequent_vd':int(b.name in sub.index),'prior_equity':int(b.name in prior.index)})
newcols=pd.DataFrame(rows)
new=old.merge(newcols,on='full_firm_id',how='left',validate='one_to_one',sort=False)
for c in ['vd_first_date','vd_last_source_date']:new[c]=new[c].fillna('')
labels_new={
'vd_initial_usd':'Table 3-1: first VD round amount, nominal USD',
'ln_vd_initial':'Table 3-2: ln(initial VD USD), positive values only',
'ln1p_vd_initial':'Alternative ln(1 + initial VD USD)',
'vd_pre_equity_usd':'Complete sum of equity strictly before first VD date, USD',
'vd_prev_equity_usd':'Latest strictly prior equity round USD; tied dates missing',
'vd_to_pre_equity':'Table 3-3: initial VD / pre-VD cumulative equity; denominator >0',
'vd_to_prev_equity':'Table 3-4: initial VD / latest prior equity round; denominator >0',
'vd_share_total_capital':'Table 3-5: initial VD / (initial VD + strictly prior equity)',
'vd_subseq_rounds':'Table 3-6: subsequent Debt Financing rounds in source snapshot',
'vd_subseq_usd':'Subsequent VD USD; none=0; any undisclosed round=missing',
'ln_vd_subseq':'ln(subsequent VD USD); zero or incomplete=missing',
'ln1p_vd_subseq':'Table 3-7 candidate: ln(1+subsequent VD USD); incomplete=missing',
'vd_cumulative_usd':'VD USD from First VD marker onward; any undisclosed round=missing',
'ln_vd_cumulative':'Table 3-8: ln(cumulative VD USD); complete positive totals only',
'ln1p_vd_cumulative':'Alternative ln(1+cumulative VD USD)',
'vd_initial_missing':'Initial VD amount undisclosed=1; controls missing',
'vd_earlier_debt_rounds':'Debt rounds before source First VD marker: timing discrepancy',
'vd_pre_equity_rounds':'Number of primary equity rounds strictly before first VD',
'vd_pre_equity_missing_n':'Number of prior equity rounds with undisclosed amounts',
'vd_prev_equity_ties_n':'Number of equity rounds on latest strictly prior equity date',
'vd_subseq_missing_n':'Number of subsequent VD rounds with undisclosed amounts',
'vd_total_missing_n':'Number of all VD rounds with undisclosed amounts',
'vd_subseq_known_usd':'Sum of DISCLOSED subsequent VD only; lower bound if incomplete',
'vd_cumulative_known_usd':'Disclosed VD USD from First VD onward; lower bound if incomplete',
'vd_same_day_equity_usd':'Same-date equity USD; separate diagnostic, excluded from prior',
'vd_same_day_equity_n':'Number of equity rounds on first VD date',
'vd_first_date':'First VD announced date, ISO YYYY-MM-DD',
'vd_last_source_date':'Latest source financing date for firm; not a censoring date'}
assert set(labels_new)==set(newcols)-{'full_firm_id'}
pd.testing.assert_frame_equal(old,new[old.columns])
tr=new[new.vd_backed.eq(1)]
assert len(tr)==1440 and tr.vd_initial_usd.notna().sum()==1235
assert tr.vd_share_total_capital.dropna().between(0,1).all()
valid=tr.vd_cumulative_usd.notna()
assert np.allclose(tr.loc[valid,'vd_cumulative_usd'],tr.loc[valid,'vd_initial_usd']+tr.loc[valid,'vd_subseq_usd'])
out=OUT/'csdid_ultimately_granted_full7316_controls_vd_intensity.dta'
new.to_stata(out,write_index=False,version=118,variable_labels={**labels,**labels_new},data_label=data_label)
check=pd.read_stata(out,convert_categoricals=False)
pd.testing.assert_frame_equal(old,check[old.columns],check_dtype=False)
pd.testing.assert_frame_equal(new,check,check_dtype=False)
newcols.to_csv(OUT/'vd_intensity_firm_values.csv',index=False,encoding='utf-8-sig')
pd.DataFrame(audit).to_csv(OUT/'vd_intensity_deal_audit.csv',index=False,encoding='utf-8-sig')
tr[list(labels_new)].describe().T.to_csv(OUT/'vd_intensity_summary.csv',encoding='utf-8-sig')
pd.DataFrame([{'variable':c,'definition':s} for c,s in labels_new.items()]).to_csv(OUT/'variable_dictionary.csv',index=False,encoding='utf-8-sig')
comp=[]
for c in ['founding_year','first_vd_year','time_first_vc','funding_rounds_ref','ln_funding_ref','prior_patent']:
 a=tr.loc[tr.vd_initial_missing.eq(0),c].dropna();b=tr.loc[tr.vd_initial_missing.eq(1),c].dropna()
 den=np.sqrt((a.var()+b.var())/2)
 comp.append(dict(variable=c,observed_n=len(a),missing_n=len(b),observed_mean=a.mean(),missing_mean=b.mean(),standardized_mean_diff=(a.mean()-b.mean())/den if den else np.nan))
for c in ['industry2','region2']:
 for v in sorted(tr[c].dropna().unique()):
  a=tr.loc[tr.vd_initial_missing.eq(0),c].dropna();b=tr.loc[tr.vd_initial_missing.eq(1),c].dropna()
  comp.append(dict(variable=f'{c}={v}',observed_n=len(a),missing_n=len(b),observed_mean=a.eq(v).mean(),missing_mean=b.eq(v).mean()))
pd.DataFrame(comp).to_csv(OUT/'observed_vs_missing_comparison.csv',index=False,encoding='utf-8-sig')
backup=BASE if backups else OUT/('original_before_intensity_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.dta')
if not backups: shutil.copy2(TARGET,backup)
shutil.copy2(out,TARGET)
print(json.dumps({'firms':len(new),'added_columns':len(labels_new),'treated':len(tr),'initial_observed':int(tr.vd_initial_usd.notna().sum()),'initial_missing':int(tr.vd_initial_usd.isna().sum()),'pre_ratio_observed':int(tr.vd_to_pre_equity.notna().sum()),'prev_ratio_observed':int(tr.vd_to_prev_equity.notna().sum()),'subsequent_complete':int(tr.vd_subseq_usd.notna().sum()),'cumulative_complete':int(tr.vd_cumulative_usd.notna().sum()),'backup':str(backup)},indent=2))
