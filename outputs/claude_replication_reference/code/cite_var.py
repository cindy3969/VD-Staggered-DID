import pandas as pd, numpy as np, json, subprocess
app=pd.read_csv('app.csv',encoding='utf-8-sig',low_memory=False)
a=app[app.forward_citations_through_2024.notna()]
g=a.groupby(['full_firm_id','filing_year']).forward_citations_through_2024
V=pd.DataFrame({'cite_mean':g.mean(),'cite_sum':g.sum()}).reset_index().rename(columns={'filing_year':'year'})
V['cite_ln_sum']=np.log1p(V.cite_sum)
p=pd.read_csv('hist_panel.csv',low_memory=False).drop(columns=['cite_mean','cite_sum','cite_ln_sum'],errors='ignore').merge(V,on=['full_firm_id','year'],how='left')
for c in ['cite_mean','cite_sum','cite_ln_sum']: p[c]=p[c].fillna(0)
p.to_csv('hist_panel.csv',index=False)
