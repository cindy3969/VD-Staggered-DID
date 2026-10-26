from pathlib import Path
import pandas as pd
import json, hashlib
from validate_vd_lenders import split_names, SOURCE

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / 'outputs/vd_lender_validation_2820'
OUT = ROOT / 'outputs/vd_lender_validation_corrected_2820'
OUT.mkdir(exist_ok=True)
sample = ROOT / 'outputs/psm_table3_7_rematch/rematched_2820_cross_section.dta'
f = pd.read_stata(sample, convert_categoricals=False)
# Re-read source; do not rely on previous sample-specific outputs for counts.
cols = ['Organization Name','Funding Type','Debt','First VD','Investor names',
        'Announced Date','Money Raised Currency (in USD)']
d = pd.read_excel(SOURCE, header=1, usecols=cols)
d['source_excel_row'] = d.index + 3
d['date'] = pd.to_datetime(d['Announced Date'], errors='coerce')
assert len(f)==2820 and f.OrganizationName.is_unique and f.VD.sum()==1410
assert set(f.OrganizationName).issubset(set(d['Organization Name']))
providers = pd.read_csv(OLD/'provider_dictionary.csv').set_index('participant_name').category.to_dict()
t = f.loc[f.VD.eq(1),'OrganizationName']
m = d[d['Organization Name'].isin(t)].copy()
q = m[m.Debt.eq(1)|m['Funding Type'].eq('Debt Financing')].copy()
q['names'] = q['Investor names'].map(split_names)
q['category'] = q.names.map(lambda ns:min((int(providers.get(n,4)) for n in ns),default=0))
q.loc[~q['Funding Type'].eq('Debt Financing'),'category']=4
q['named'] = q.names.map(bool)
q['prior_series']=False
q['seed_or_same_day_only']=False
for name,g in m.groupby('Organization Name'):
    series=g[g['Funding Type'].str.match(r'^Series [A-Z]',na=False)]
    seeds=g[g['Funding Type'].isin(['Seed','Pre-Seed','Angel'])]
    for i,row in q[q['Organization Name'].eq(name)].iterrows():
        prior=bool(series.date.lt(row.date).any())
        q.loc[i,'prior_series']=prior
        q.loc[i,'seed_or_same_day_only']=not prior and bool(seeds.date.lt(row.date).any() or series.date.eq(row.date).any())
q['positive_amount']=pd.to_numeric(q['Money Raised Currency (in USD)'],errors='coerce').gt(0)
first=q[q['First VD'].eq(1)].copy()
assert len(first)==1410 and first['Organization Name'].is_unique
anon=first[~first.named]
result={'matched':len(f),'treated':len(t),'first_named':int(first.named.sum()),
 'first_missing':len(anon),'any_named':q.loc[q.named,'Organization Name'].nunique(),
 'first_categories':first.category.value_counts().sort_index().to_dict(),
 'anonymous_first':{'debt_type':int(anon['Funding Type'].eq('Debt Financing').sum()),
 'prior_series':int(anon.prior_series.sum()),'seed_or_same_day_only':int(anon.seed_or_same_day_only.sum()),
 'no_prior_series_seed_or_same_day':int((~anon.prior_series & ~anon.seed_or_same_day_only).sum()),
 'positive_amount':int(anon.positive_amount.sum()),'date_reported':int(anon.date.notna().sum())},
 'deals':len(q),'deal_categories':q.category.value_counts().sort_index().to_dict(),
 'source':str(SOURCE),'sample':str(sample),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()}
first.drop(columns='names').to_csv(OUT/'first_transaction_audit.csv',index=False,encoding='utf-8-sig')
(OUT/'statistics.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
