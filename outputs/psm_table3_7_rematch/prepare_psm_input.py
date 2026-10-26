import pandas as pd
p=r"C:\Users\user\Documents\VD\outputs\psm_final_2820_package\latest_code_caliper005\spec_A_psmatch2_direct_full7316.csv"
o=r"C:\Users\user\Documents\VD\outputs\psm_table3_7_rematch\psm_input_7316.dta"
d=pd.read_csv(p)
keep=['Organization Name','Organization Name URL','name_key','VD_Backing','ln_Total_Funding_Amount_FirstVD','NumberOfFunding_Rounds_FirstVD','Patents_VD','Founding_Year','TimeToFirst_VC','Region2','Industry2','ln_Total_Funding_Amount_T3']
d=d[keep].rename(columns={'Organization Name':'OrganizationName','Organization Name URL':'OrganizationURL'})
for c in d.select_dtypes(include='object'): d[c]=d[c].fillna('').astype(str)
d.to_stata(o,write_index=False,version=118)
