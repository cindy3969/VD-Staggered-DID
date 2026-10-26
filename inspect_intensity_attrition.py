import pandas as pd
p='outputs/vd_intensity/tables_3_1_to_3_7/analysis_panel.dta'
f=pd.read_stata(p,convert_categoricals=False)
c=['outcome','vd_initial_usd','prior','early','post','prior_patent_l1','lag_early','ln1p_cum_funding_l1','ln1p_rounds_l1']
z=f.dropna(subset=c)
g=z.groupby('full_firm_id').post.agg(['min','max','size'])
print('usable firms',len(g),'rows',len(z));print(g.groupby(['min','max']).agg(firms=('size','size'),rows=('size','sum')).to_string())
print('singleton firms',g['size'].eq(1).sum())
