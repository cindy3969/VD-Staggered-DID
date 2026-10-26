import pandas as pd
x=pd.read_pickle('deals_intensity_cache.pkl');x['Organization Name']=x['Organization Name'].astype(str)
cols=['Organization Name','deal no','Announced Date','Funding Type','Debt','First VD','Money Raised Currency (in USD)']
print(x[x.duplicated(['Organization Name','deal no'],keep=False)][cols].to_string(index=False))
print(x.loc[x['First VD'].eq(1), 'Funding Type'].value_counts())
print(x.loc[x.Debt.eq(1),'Funding Type'].value_counts())
f=x[x['First VD'].eq(1)&~x['Organization Name'].isin(['Dermira','Eargo'])];print('initial',len(f),f['Money Raised Currency (in USD)'].notna().sum());print(f[cols].head(12).to_string(index=False))
print('negative',pd.to_numeric(x['Money Raised Currency (in USD)'],errors='coerce').lt(0).sum())
