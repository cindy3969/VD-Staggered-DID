import re
import numpy as np
import pandas as pd

PRE = r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms\exact matched sample v6 unmatched.xlsx"
FINAL = r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms\251111 2820 cross sectional.dta"
OUT = r"C:\Users\user\Documents\VD\outputs\psm_final_2820_package\psm_specification_overlap.csv"

def key(x): return re.sub(r"[^a-z0-9]+", "", str(x).casefold())

def logit_score(X, y):
    xv, yv = X.to_numpy(float), y.to_numpy(float)
    b = np.zeros(xv.shape[1])
    for _ in range(200):
        eta = np.clip(xv @ b, -30, 30); p = 1/(1+np.exp(-eta))
        w = np.clip(p*(1-p), 1e-9, None); z = eta+(yv-p)/w; sw=np.sqrt(w)
        bn=np.linalg.pinv(xv*sw[:,None])@(z*sw)
        if np.max(np.abs(bn-b))<1e-9: b=bn; break
        b=bn
    return 1/(1+np.exp(-np.clip(xv@b,-30,30)))

def match(e, order):
    t=e[e.VD_Backing.eq(1)].copy(); c=e[e.VD_Backing.eq(0)].copy()
    lo=max(t.ps.min(),c.ps.min()); hi=min(t.ps.max(),c.ps.max())
    t=t[t.ps.between(lo,hi)]; c=c[c.ps.between(lo,hi)]
    if order=='ascending': t=t.sort_values(['ps','name_key'])
    elif order=='descending': t=t.sort_values(['ps','name_key'],ascending=[False,True])
    available=c.index.to_numpy(); cp=c.ps.to_numpy(); chosen=[]
    for _,r in t.iterrows():
        if len(cp) == 0: break
        j=int(np.argmin(np.abs(cp-r.ps))); chosen.append(int(available[j])); available=np.delete(available,j); cp=np.delete(cp,j)
    return set(e.loc[chosen,'name_key']),len(chosen)

d=pd.read_excel(PRE); d['name_key']=d['Organization Name'].map(key)
d.loc[d.name_key.isin([key('Dermira'),key('Eargo')]),'VD_Backing']=1
d.loc[d.name_key.isin([key('Cortex'),key('Nomi1')]),'VD_Backing']=0
d['lnfund']=np.log1p(d.Total_Funding_Amount_FirstVD)
f=pd.read_stata(FINAL,convert_categoricals=False); f['name_key']=f.OrganizationName.map(key)
old=set(f.loc[f.VD.eq(0),'name_key'])

specs={
 'manuscript_7': (['Founding_Year','Region2','Industry2'],['lnfund','NumberOfFunding_Rounds_FirstVD','Grant_VD','TimeToFirst_VC']),
 'plus_vd_year': (['Founding_Year','VD Year','Region2','Industry2'],['lnfund','NumberOfFunding_Rounds_FirstVD','Grant_VD','TimeToFirst_VC']),
 'plus_time_to_vd': (['Founding_Year','Region2','Industry2'],['lnfund','NumberOfFunding_Rounds_FirstVD','Grant_VD','TimeToFirst_VC','TimeToFirst_VD']),
 'plus_both': (['Founding_Year','VD Year','Region2','Industry2'],['lnfund','NumberOfFunding_Rounds_FirstVD','Grant_VD','TimeToFirst_VC','TimeToFirst_VD']),
}
rows=[]
for name,(cats,conts) in specs.items():
    z=d.dropna(subset=cats+conts).copy()
    C=pd.get_dummies(z[cats].astype(str),drop_first=True,dtype=float); X=pd.concat([C,z[conts].astype(float)],axis=1); X.insert(0,'const',1.)
    z['ps']=logit_score(X,z.VD_Backing.astype(int))
    for order in ['original','ascending','descending']:
        controls,nt=match(z,order); ov=len(old&controls)
        rows.append({'specification':name,'order':order,'eligible_treated':int(z.VD_Backing.sum()),'matched_treated':nt,'old_control_overlap':ov,'overlap_pct':ov/1410*100})
res=pd.DataFrame(rows); res.to_csv(OUT,index=False,encoding='utf-8-sig'); print(res.to_string(index=False))
