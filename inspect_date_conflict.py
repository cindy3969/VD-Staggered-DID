import pandas as pd
x=pd.read_pickle('deals_intensity_cache.pkl');x['Organization Name']=x['Organization Name'].astype(str);x['date']=pd.to_datetime(x['Announced Date'])
for n,z in x.groupby('Organization Name'):
 a=z[z['First VD'].eq(1)]
 if len(a)!=1 or n in ['Dermira','Eargo']:continue
 d=z[z['Funding Type'].eq('Debt Financing')]
 if (d.date<a.iloc[0].date).any():print(n);print(d[['deal no','date','First VD','Money Raised Currency (in USD)']].to_string(index=False))
