import pandas as pd
from pathlib import Path
r=Path('outputs')
i=pd.read_stata(r/'csdid_ultimately_granted_primary/csddid.dta') if False else pd.read_stata(r/'csdid_ultimately_granted_primary/csdid_ultimately_granted_full7316_controls.dta',convert_categoricals=False)
for p in [r/'psm_final_2820_package/table3_current_2820_cross_section_v2.dta',r/'psm_table3_7_rematch/rematched_2820_cross_section.dta']:
 f=pd.read_stata(p,convert_categoricals=False)
 print('FILE',p,'shape',f.shape)
 cols=[c for c in f if any(s in c.lower() for s in ['organization','vd','firm_id'])]
 print(cols)
 for c in ['VD','VD_Backing','vd_backed']:
  if c in f:
   print(c,f[c].value_counts().to_dict())
 name=next((c for c in ['OrganizationName','organization_name','Organization Name'] if c in f),None)
 treat=next((c for c in ['VD','VD_Backing','vd_backed'] if c in f),None)
 if name and treat:
  z=f.loc[f[treat].eq(1),[name]].rename(columns={name:'organization_name'}).merge(i[['organization_name','vd_initial_usd','vd_cumulative_usd']],on='organization_name',how='left',indicator=True,validate='one_to_one')
  print('MATCH',z._merge.value_counts().to_dict(),'initial',z.vd_initial_usd.notna().sum(),'missing',z.vd_initial_usd.isna().sum(),'cumulative',z.vd_cumulative_usd.notna().sum())
print('AUDIT');print(pd.read_csv(r/'vd_intensity/tables_3_1_to_3_7/sample_audit.csv').to_string(index=False))
