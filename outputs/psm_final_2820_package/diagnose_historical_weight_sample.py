import numpy as np
import pandas as pd

ROOT=r"C:\Users\user\Documents\VD\outputs\psm_final_2820_package"
f=ROOT+r"\v4_rebuilt_matching_covariates_7316_without_patents.csv"
d=pd.read_csv(f)
d['treated']=d.vd_backed_raw.astype(int)
d['matched']=d.historical_weight.astype(int)

X=pd.DataFrame(index=d.index)
X['Log funding amount at reference year']=pd.to_numeric(d.ln_funding_amount_ref,errors='coerce')
X['Funding rounds at reference year']=pd.to_numeric(d.funding_rounds_ref_rebuilt,errors='coerce')
X['Founding year']=pd.to_numeric(d.founding_year,errors='coerce')
X['Time to first VC']=pd.to_numeric(d.time_to_first_vc,errors='coerce')
for c in ['California','Massachusetts','New York']:
    X['Region: '+c]=(d.region2==c).astype(float)
for c in ['Bio/Healthcare','Hardware/Manufacturing/DeepTech','Software/IT services']:
    X['Industry: '+c]=(d.industry2==c).astype(float)

def stats(x,t,mask):
    a=x[mask & t.eq(1)].dropna(); b=x[mask & t.eq(0)].dropna()
    va=a.var(ddof=1); vb=b.var(ddof=1); pool=np.sqrt((va+vb)/2)
    return {'treated_n':len(a),'control_n':len(b),'treated_mean':a.mean(),'control_mean':b.mean(),
            'smd':100*(a.mean()-b.mean())/pool if pool>0 else np.nan,
            'variance_ratio':va/vb if vb>0 else np.nan}
rows=[]
for name in X:
    pre=stats(X[name],d.treated,pd.Series(True,index=d.index))
    post=stats(X[name],d.treated,d.matched.eq(1))
    rows.append({'covariate':name,**{'pre_'+k:v for k,v in pre.items()},**{'post_'+k:v for k,v in post.items()}})
out=pd.DataFrame(rows)
out['abs_smd_before']=out.pre_smd.abs(); out['abs_smd_after']=out.post_smd.abs()
out.to_csv(ROOT+r"\historical_weight_balance_diagnostics_6vars.csv",index=False,encoding='utf-8-sig')
print(out[['covariate','pre_smd','post_smd','pre_variance_ratio','post_variance_ratio']].to_string(index=False))
print('\nmax abs SMD before',out.abs_smd_before.max(),'after',out.abs_smd_after.max())
print('mean abs SMD before',out.abs_smd_before.mean(),'after',out.abs_smd_after.mean())
