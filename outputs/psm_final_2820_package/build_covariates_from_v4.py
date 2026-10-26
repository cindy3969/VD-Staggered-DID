import re
import numpy as np
import pandas as pd

V4=r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms\2010 2015 Crunchbase deals merged_v4.xlsx"
FINAL=r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms\251111 2820 cross sectional.dta"
ROOT=r"C:\Users\user\Documents\VD\outputs\psm_final_2820_package"
def key(x): return re.sub(r'[^a-z0-9]+','',str(x).casefold())
def first_valid(s):
    for v in s:
        if pd.notna(v) and v not in ('','`'): return v
    return np.nan

d=pd.read_excel(V4,header=1)
d['name_key']=d['Organization Name'].map(key)
f=pd.read_stata(FINAL); f['name_key']=f.OrganizationName.map(key)

# Inspect raw-to-final categorical mappings on the archived matched sample.
base=d.sort_values(['name_key','Announced Date']).groupby('name_key',as_index=False).first()
m=base.merge(f[['name_key','Region2','Industry2']],on='name_key',how='inner')
print('\nRegion raw -> Region2')
print(pd.crosstab(m.Region,m.Region2).to_string())
print('\nIndustry Classification raw -> Industry2 (top rows)')
ct=pd.crosstab(m['Industry Classification'],m.Industry2)
print(ct.to_string())

g=d.sort_values(['name_key','Announced Date']).groupby('name_key')
firm=pd.DataFrame({
 'organization_name':g['Organization Name'].first(),
 'organization_url':g['Organization Name URL'].first(),
 'historical_weight':g['weight'].max().fillna(0).astype(int),
 'vd_backed_raw':g.VD_Backing.max().fillna(0).astype(int),
 'founding_year':g['found year'].first(),
 'actual_vd_year':g.VD.apply(first_valid),
 'funding_rounds_ref':g.NumberOfFunding_Rounds_FirstVD.apply(first_valid),
 'funding_amount_ref':g.TotalFundingAmount_FirstVD.apply(first_valid),
 'time_to_first_vc':g.TimeToFirst_VC.apply(first_valid),
 'region_raw':g.Region.first(),
 'industry_groups_raw':g['Industry Groups'].first(),
 'industry_class_raw':g['Industry Classification'].first(),
}).reset_index()
firm['reference_year']=np.where(firm.vd_backed_raw.eq(1),pd.to_numeric(firm.actual_vd_year,errors='coerce'),pd.to_numeric(firm.founding_year,errors='coerce')+5)
# Preserve the treatment definition in the archived 2,820 analysis.
firm.loc[firm.organization_name.isin(['Dermira','Eargo']),'vd_backed_raw']=1
firm.loc[firm.organization_name.isin(['Cortex','Nomi1']),'vd_backed_raw']=0
# For every archived matched firm, the final cross-sectional treatment flag is
# authoritative. This resolves one additional name/history inconsistency in V4.
arch_vd=f.set_index('name_key')['VD'].to_dict()
mask_arch=firm.name_key.isin(arch_vd)
firm.loc[mask_arch,'vd_backed_raw']=firm.loc[mask_arch,'name_key'].map(arch_vd).astype(int)
# The current deal file no longer flags Dermira/Eargo as VD. Recover their
# archived first-VD year solely to reproduce the historical treatment rule.
arch_vdyear=f.set_index('name_key')['VDyear'].to_dict()
mask_arch_t=mask_arch & firm.vd_backed_raw.eq(1)
firm.loc[mask_arch_t,'actual_vd_year']=firm.loc[mask_arch_t,'name_key'].map(arch_vdyear)
firm['reference_year']=np.where(firm.vd_backed_raw.eq(1),pd.to_numeric(firm.actual_vd_year,errors='coerce'),pd.to_numeric(firm.founding_year,errors='coerce')+5)

# Recompute financing covariates consistently for every firm from the deals:
# all observed financing rounds through the end of the reference calendar year.
d['deal_year_num']=pd.to_numeric(d['Deal year'],errors='coerce')
d['deal_amount_num']=pd.to_numeric(d['Money Raised Currency (in USD)'],errors='coerce').fillna(0)
d=d.merge(firm[['name_key','reference_year']],on='name_key',how='left')
at_ref=d[d.deal_year_num.le(d.reference_year)].groupby('name_key').agg(
    funding_amount_ref_rebuilt=('deal_amount_num','sum'),
    funding_rounds_ref_rebuilt=('deal_year_num','size')
)
firm=firm.merge(at_ref,left_on='name_key',right_index=True,how='left')
firm['ln_funding_amount_ref']=np.log1p(pd.to_numeric(firm.funding_amount_ref_rebuilt,errors='coerce'))
firm['region2']=np.where(firm.region_raw.isin(['California','Massachusetts','New York']),firm.region_raw,'Other')

# Derive the broad industry group using the observed deterministic mapping in
# the archived matched sample, falling back to keywords only where a raw class
# was absent from the archived sample.
map_counts=(m.groupby(['Industry Classification','Industry2'],observed=True).size().rename('n').reset_index())
imap=map_counts.sort_values(['Industry Classification','n']).groupby('Industry Classification',observed=True).tail(1).set_index('Industry Classification').Industry2.to_dict()
firm['industry2']=firm.industry_class_raw.map(imap)
txt=(firm.industry_groups_raw.fillna('').astype(str)+' '+firm.industry_class_raw.fillna('').astype(str)).str.lower()
firm.loc[firm.industry2.isna() & txt.str.contains('health|bio|medical|pharma|therapeut|clinical'), 'industry2']='Bio/Healthcare'
firm.loc[firm.industry2.isna() & txt.str.contains('hardware|manufactur|energy|transport|science|engineering|industrial'), 'industry2']='Hardware/Manufacturing/DeepTech'
firm.loc[firm.industry2.isna() & txt.str.contains('software|information technology|internet|data|artificial intelligence'), 'industry2']='Software/IT services'
firm['industry2']=firm.industry2.fillna('Other')

# Stata-ready numeric encodings follow the archived value-label ordering.
firm['region2_n']=firm.region2.map({'California':1,'Massachusetts':2,'New York':3,'Other':4})
firm['industry2_n']=firm.industry2.map({'Bio/Healthcare':1,'Hardware/Manufacturing/DeepTech':2,'Other':3,'Software/IT services':4})

# Merge archived final values for direct validation.
cols=['name_key','VD','Founding_Year','MoneyRaised_VD','NumofFundingRounds_VD','TimetoFirstVC','Region2','Industry2','patentbygranted']
z=firm.merge(f[cols],on='name_key',how='left',suffixes=('_rebuilt','_final'))
for a,b in [('funding_amount_ref','MoneyRaised_VD'),('funding_rounds_ref','NumofFundingRounds_VD'),('time_to_first_vc','TimetoFirstVC'),('founding_year','Founding_Year')]:
 x=pd.to_numeric(z[a],errors='coerce'); y=pd.to_numeric(z[b],errors='coerce'); ok=x.notna()&y.notna(); print(a,'vs',b,'n',ok.sum(),'exact',np.isclose(x[ok],y[ok]).sum(),'pct',np.isclose(x[ok],y[ok]).mean()*100 if ok.sum() else np.nan)
print('region exact', (z.loc[z.Region2.notna(),'region2']==z.loc[z.Region2.notna(),'Region2'].astype(str)).mean())
print('industry exact', (z.loc[z.Industry2.notna(),'industry2']==z.loc[z.Industry2.notna(),'Industry2'].astype(str)).mean())

firm.to_csv(ROOT+r'\v4_rebuilt_matching_covariates_7316_without_patents.csv',index=False,encoding='utf-8-sig')
stata=firm.copy()
for c in stata.select_dtypes(include='object'):
    stata[c]=stata[c].where(stata[c].notna(),'').astype(str)
stata.to_stata(ROOT+r'\v4_rebuilt_matching_covariates_7316_without_patents.dta',write_index=False,version=118)
z.to_csv(ROOT+r'\v4_covariate_validation_against_251111.csv',index=False,encoding='utf-8-sig')
