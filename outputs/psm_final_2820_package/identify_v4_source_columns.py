import re
import numpy as np
import pandas as pd

V4=r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms\2010 2015 Crunchbase deals merged_v4.xlsx"
FINAL=r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms\251111 2820 cross sectional.dta"
OUT=r"C:\Users\user\Documents\VD\outputs\psm_final_2820_package\v4_source_column_match_rates.csv"
def key(x): return re.sub(r'[^a-z0-9]+','',str(x).casefold())
d=pd.read_excel(V4,header=1)
d['key']=d['Organization Name'].map(key)
f=pd.read_stata(FINAL,convert_categoricals=False); f['key']=f.OrganizationName.map(key)
targets=['MoneyRaised_VD','NumofFundingRounds_VD','Founding_Year','TimetoFirstVC','patentbygranted','VDyear']
num=[]
for c in d.columns:
    x=pd.to_numeric(d[c],errors='coerce')
    if x.notna().sum()>100: num.append(c)
rows=[]
for c in num:
    x=pd.to_numeric(d[c],errors='coerce')
    tmp=pd.DataFrame({'key':d.key,'x':x,'dealyear':pd.to_numeric(d.get('Deal year'),errors='coerce')})
    aggs={
      'first':tmp.groupby('key').x.first(), 'last':tmp.groupby('key').x.last(),
      'min':tmp.groupby('key').x.min(), 'max':tmp.groupby('key').x.max()
    }
    for agg,s in aggs.items():
      z=f[['key']+targets].merge(s.rename('src'),left_on='key',right_index=True,how='left')
      for t in targets:
        y=pd.to_numeric(z[t],errors='coerce'); ok=y.notna()&z.src.notna()
        if ok.sum(): rows.append({'target':t,'source_col':str(c),'aggregation':agg,'n':int(ok.sum()),'exact':int(np.isclose(y[ok],z.loc[ok,'src'],rtol=1e-10,atol=1e-8).sum()),'pct':float(np.isclose(y[ok],z.loc[ok,'src'],rtol=1e-10,atol=1e-8).mean()*100)})
res=pd.DataFrame(rows).sort_values(['target','pct'],ascending=[True,False]); res.to_csv(OUT,index=False,encoding='utf-8-sig')
for t in targets:
 print('\n',t); print(res[res.target.eq(t)].head(12).to_string(index=False))
