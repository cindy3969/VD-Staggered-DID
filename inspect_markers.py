import pandas as pd
x=pd.read_pickle('deals_intensity_cache.pkl')
for c in ['VD','First VD','First VD.1','Debt','VD_Backing']:
 print(c,x[c].value_counts(dropna=False).to_dict())
print(pd.crosstab(x['Funding Type'],x['VD']).to_string())
print(x.loc[x['VD'].eq(1),['Organization Name','deal no','Announced Date','Funding Type','VD','First VD','First VD.1','Money Raised Currency (in USD)']].head(15).to_string(index=False))
f=pd.read_stata('outputs/csdid_ultimately_granted_primary/csdid_ultimately_granted_full7316_controls.dta'); print('treated',f.vd_backed.sum());print('unmatched',set(f.organization_name)-set(x['Organization Name']))
print('duplicate',x.duplicated(['Organization Name','deal no']).sum())
