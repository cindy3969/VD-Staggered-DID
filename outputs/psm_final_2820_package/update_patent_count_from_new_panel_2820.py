import re
import numpy as np
import pandas as pd

PANEL=r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms\firm_year_with_patents_2820.xlsx"
FINAL=r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms\251111 2820 cross sectional.dta"
ROOT=r"C:\Users\user\Documents\VD\outputs\psm_final_2820_package"
def key(x): return re.sub(r'[^a-z0-9]+','',str(x).casefold())

p=pd.read_excel(PANEL,usecols=['OrganizationName','VDyear','deal year','patentbygranted','cum_patentbygranted'])
p['name_key']=p.OrganizationName.map(key)
p['deal year']=pd.to_numeric(p['deal year'],errors='coerce'); p.VDyear=pd.to_numeric(p.VDyear,errors='coerce')

# Matching covariate measured at the reference year: cumulative applications
# filed through that year that were ultimately granted.
at=p[p['deal year'].eq(p.VDyear)].copy()
at=at[['name_key','OrganizationName','VDyear','cum_patentbygranted']].drop_duplicates('name_key')
at=at.rename(columns={'cum_patentbygranted':'pre_vd_granted_apps_updated'})

f=pd.read_stata(FINAL,convert_categoricals=False); f['name_key']=f.OrganizationName.map(key)
z=f.merge(at,on='name_key',how='left',suffixes=('','_panel'))
z['pre_vd_granted_apps_updated']=z.pre_vd_granted_apps_updated.fillna(0)
z['patent_count_changed']=~np.isclose(pd.to_numeric(z.patentbygranted,errors='coerce').fillna(0),z.pre_vd_granted_apps_updated)
print('firms',len(z),'panel matched',z.OrganizationName_panel.notna().sum())
print('old-new exact',(~z.patent_count_changed).sum(),'changed',z.patent_count_changed.sum())
print(z[['patentbygranted','pre_vd_granted_apps_updated']].describe().to_string())
z.to_csv(ROOT+r'\matched2820_updated_pre_vd_patent_counts.csv',index=False,encoding='utf-8-sig')
for c in z.select_dtypes(include='object'): z[c]=z[c].where(z[c].notna(),'').astype(str)
z.to_stata(ROOT+r'\matched2820_updated_pre_vd_patent_counts.dta',write_index=False,version=118)
