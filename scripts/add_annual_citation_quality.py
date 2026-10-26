from pathlib import Path
import pandas as pd
import numpy as np
import json
R=Path(r'C:\Users\user\Documents\VD')
S=R/'outputs/table4_window3_39249_20261019'
O=R/'outputs/csdid_all_applications_corrected/citation_quality_20261019'
O.mkdir(parents=True,exist_ok=True)
grid=pd.read_csv(S/'application_year_corrected.csv',dtype={'application_id':'string'})
first_grants=pd.read_csv(R/'outputs/table2_forward_citation_year_methods_39249/application_citation_year_grid.csv',usecols=['application_id','grant_date'],dtype={'application_id':'string'}).drop_duplicates('application_id')
# Use the first linked grant even if that grant has no incoming citations.
# Taking dates from citation edges alone misses uncited earlier grant numbers.
dates=first_grants.set_index('application_id').grant_date
grid['grant_year']=pd.to_datetime(grid.application_id.map(dates)).dt.year
grid['cum_cites']=grid.groupby('application_id').n_cites.cumsum()
grid['rate']=np.where(grid.year.ge(grid.grant_year),grid.cum_cites/(grid.year-grid.grant_year+1),0.)
rate_mean=grid.groupby(['filing_year','year']).rate.transform('mean')
grid['rate_norm']=np.divide(grid.rate,rate_mean,out=np.zeros(len(grid)),where=rate_mean.gt(0))
a=grid.groupby(['full_firm_id','application_id','filing_year','cpc3'],as_index=False).agg(v1=('fwd_norm_cohort','sum'),v2=('fwd_norm_cohort_cpc','sum'),v3=('rate_norm','last'),raw=('n_cites','sum'))
mean=a.groupby(['filing_year','cpc3']).raw.transform('mean')
a['v4']=np.divide(a.raw,mean,out=np.zeros(len(a)),where=mean.gt(0))
assert len(a)==34855
a.to_csv(O/'application_quality_corrected.csv',index=False)
f=a.groupby(['full_firm_id','filing_year']).agg(citation_quality_npat=('application_id','nunique'),**{f'norm_cite_perpat_v{k}':(f'v{k}','mean') for k in range(1,5)}).reset_index().rename(columns={'filing_year':'year'})
p=pd.read_stata(R/'outputs/csdid_all_applications_corrected/firm_year_all_applications_and_truncation_specs.dta',convert_categoricals=False)
source=pd.read_csv(R/'outputs/csdid_union_corrected_3yr/application_level_union_corrected_visible_mismatches.csv',usecols=['full_firm_id','organization_name']).drop_duplicates()
names=p[['full_firm_id','organization_name']].drop_duplicates().merge(source,on='full_firm_id')
assert names.organization_name_x.eq(names.organization_name_y).all(), 'ID/name crosswalk mismatch'
x=p[['full_firm_id','year']].merge(f,on=['full_firm_id','year'],how='left',validate='one_to_one')
x.citation_quality_npat=x.citation_quality_npat.fillna(0).astype(int)
for k in range(1,5):
    assert x.loc[x.citation_quality_npat.eq(0),f'norm_cite_perpat_v{k}'].isna().all()
    assert x.loc[x.citation_quality_npat.gt(0),f'norm_cite_perpat_v{k}'].notna().all()
x.to_csv(O/'annual_quality_addon.csv',index=False)
x.to_stata(O/'annual_quality_addon.dta',write_index=False,version=118,variable_labels={f'norm_cite_perpat_v{k}':f'Annual filing-cohort mean normalized citation quality v{k}; NOT log, NOT win3' for k in range(1,5)})
q={'panel_rows':len(x),'panel_firms':x.full_firm_id.nunique(),'rows_with_patents':int(x.citation_quality_npat.gt(0).sum()),'firms_with_patents':x.loc[x.citation_quality_npat.gt(0),'full_firm_id'].nunique(),'application_universe':39249,'granted_applications':len(a),'definition':'Year = focal application filing year. Mean across ultimately granted applications filed by firm in that year; normalized citation measures observed through 2024. No rolling window; no log.','missing':'No granted applications in filing year => missing, preserving original v1-v4 conditional quality convention.'}
(O/'QA.json').write_text(json.dumps(q,indent=2),encoding='utf-8')
print(json.dumps(q,indent=2))
