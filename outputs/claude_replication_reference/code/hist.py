import pandas as pd, numpy as np
p=pd.read_csv('csdid_full7316_all_published_A1_applications_panel_1.csv',encoding='utf-8-sig',low_memory=False)
p['G']=p.g_first_vd.fillna(0).astype(int)
p=p[(p.year<=2024)&~((p.G>0)&(p.G==p.founding_year))].copy()
p=p.sort_values(['full_firm_id','year'])
p['cum_gr']=p.groupby('full_firm_id').ultimately_granted_filings.cumsum()
base=p[p.year==p.G-1][['full_firm_id','cum_gr','latest_stage']]
base['prior']=(base.cum_gr>0).astype(int)
early_set={'Seed','Early Stage Venture','Convertible Note','Grant','Private Equity','Non-equity Assistance'}
base['early']=(base.latest_stage.isna()|base.latest_stage.isin(early_set)).astype(int)
p=p.merge(base[['full_firm_id','prior','early']],on='full_firm_id',how='left')
p.to_csv('hist_panel.csv',index=False)
