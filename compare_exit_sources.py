import pandas as pd, re, numpy as np

root=r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms"
old=pd.read_stata(root+r"\260122 winsorization.dta",convert_categoricals=False)
deals=pd.read_excel(root+r"\2010 2015 Crunchbase deals merged_v4.xlsx",header=1)
def key(x): return re.sub(r"[^a-z0-9]","",str(x).casefold())
old['k']=old.OrganizationName.map(key); deals['k']=deals['Organization Name'].map(key)
g=deals.groupby('k').agg(last_deal_year=('Deal year','max'),funding_status=('Funding Status','first'),operating=('Operating Status','first'),ipo_date=('IPO Date','first')).reset_index()
g['ipo_year']=pd.to_datetime(g.ipo_date,errors='coerce').dt.year
x=old.merge(g,on='k',how='left')
for c in ['exityear','exityear2','exityear3','exittype','exittype2','exittype3','acq3','public3','badexit3']:
    if c in x: print('\n',c,x[c].value_counts(dropna=False).head(20).to_dict())
print('\nexit vs source')
print(x[['OrganizationName','VD','VDyear','exityear','exittype','last_deal_year','funding_status','operating','ipo_year','acq3','public3','badexit3']].dropna(subset=['exityear']).head(40).to_string(index=False))
print('equal exit lastdeal', (x.exityear==x.last_deal_year).mean(), 'nonmiss',x.exityear.notna().sum())
print(pd.crosstab(x.exittype,x.funding_status,dropna=False).to_string())
