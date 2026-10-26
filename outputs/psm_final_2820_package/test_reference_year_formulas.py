import re
import pandas as pd
import numpy as np

V4=r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms\2010 2015 Crunchbase deals merged_v4.xlsx"
FINAL=r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms\251111 2820 cross sectional.dta"
def key(x): return re.sub(r'[^a-z0-9]+','',str(x).casefold())
d=pd.read_excel(V4,header=1); d['key']=d['Organization Name'].map(key); d['date']=pd.to_datetime(d['Announced Date'],errors='coerce'); d['amt']=pd.to_numeric(d['Money Raised Currency (in USD)'],errors='coerce').fillna(0)
f=pd.read_stata(FINAL,convert_categoricals=False); f['key']=f.OrganizationName.map(key)
rows=[]
for k,g in d.groupby('key',sort=False):
    founding=pd.to_numeric(g['found year'],errors='coerce').dropna().iloc[0]
    oldvd=f.loc[f.key.eq(k),'VD']; vd=int(oldvd.iloc[0]) if len(oldvd) else int(pd.to_numeric(g.VD_Backing,errors='coerce').fillna(0).max())
    if vd:
        fd=g.loc[pd.to_numeric(g['First VD'],errors='coerce').eq(1),'date']
        cutoff=fd.min() if len(fd) else pd.Timestamp(int(pd.to_numeric(g.VD,errors='coerce').dropna().iloc[0]),12,31)
        vy=pd.to_numeric(g.VD,errors='coerce').dropna()
        cutoff_yearend=pd.Timestamp(int(vy.iloc[0]) if len(vy) else cutoff.year,12,31)
    else:
        cutoff=pd.Timestamp(int(founding+5),12,31); cutoff_yearend=cutoff
    q=g[g.date.le(cutoff)]
    qy=g[g.date.le(cutoff_yearend)]
    rows.append({'key':k,'ref_year':cutoff.year,'sum_all':q.amt.sum(),'rounds_all':len(q),'rounds_amount':q.amt.ne(0).sum(),'sum_yearend':qy.amt.sum(),'rounds_yearend':len(qy),'sum_equityonly':q.loc[q['Equity Only Funding'].eq('Yes'),'amt'].sum(),'rounds_equityonly':q['Equity Only Funding'].eq('Yes').sum()})
r=pd.DataFrame(rows); z=f.merge(r,on='key')
for vd in [0,1]:
 print('\nVD',vd)
 q=z[z.VD.eq(vd)]
 for a,t in [('sum_all','MoneyRaised_VD'),('sum_yearend','MoneyRaised_VD'),('sum_equityonly','MoneyRaised_VD'),('rounds_all','NumofFundingRounds_VD'),('rounds_yearend','NumofFundingRounds_VD'),('rounds_amount','NumofFundingRounds_VD'),('rounds_equityonly','NumofFundingRounds_VD')]:
  x=pd.to_numeric(q[a],errors='coerce'); y=pd.to_numeric(q[t],errors='coerce'); ok=x.notna()&y.notna(); eq=np.isclose(x[ok],y[ok]); print(a,t,eq.sum(),len(eq),round(eq.mean()*100,2),'maxdiff',float((x[ok]-y[ok]).abs().max()))
