import numpy as np
import pandas as pd

ROOT=r"C:\Users\user\Documents\VD\outputs\psm_final_2820_package"
SRC=ROOT+r"\v4_rebuilt_matching_covariates_7316_without_patents.csv"

d=pd.read_csv(SRC)
d['treated']=d.vd_backed_raw.astype(int)
d['old_match']=d.historical_weight.fillna(0).astype(int)

cats=pd.get_dummies(
    d[['founding_year','region2','industry2']].astype(str),
    drop_first=True,dtype=float
)
cont=d[['ln_funding_amount_ref','funding_rounds_ref_rebuilt','time_to_first_vc']].apply(pd.to_numeric,errors='coerce')
X=pd.concat([cats,cont],axis=1)
complete=X.notna().all(axis=1)
e=d.loc[complete].copy(); X=X.loc[complete].copy()
X.insert(0,'const',1.0)

def logit_score(X,y):
    xv=X.to_numpy(float); yv=y.to_numpy(float); b=np.zeros(xv.shape[1])
    for _ in range(300):
        eta=np.clip(xv@b,-30,30); p=1/(1+np.exp(-eta))
        w=np.clip(p*(1-p),1e-9,None); z=eta+(yv-p)/w; sw=np.sqrt(w)
        bn=np.linalg.pinv(xv*sw[:,None])@(z*sw)
        if np.max(np.abs(bn-b))<1e-10: b=bn; break
        b=bn
    return 1/(1+np.exp(-np.clip(xv@b,-30,30)))

e['pscore_6var']=logit_score(X,e.treated)
t=e[e.treated.eq(1)]; c=e[e.treated.eq(0)]
lo=max(t.pscore_6var.min(),c.pscore_6var.min()); hi=min(t.pscore_6var.max(),c.pscore_6var.max())
e['common_support_6var']=e.pscore_6var.between(lo,hi).astype(int)

def greedy(order):
    tt=e[(e.treated.eq(1))&(e.common_support_6var.eq(1))].copy()
    cc=e[(e.treated.eq(0))&(e.common_support_6var.eq(1))].copy()
    if order=='ascending': tt=tt.sort_values(['pscore_6var','name_key'])
    elif order=='descending': tt=tt.sort_values(['pscore_6var','name_key'],ascending=[False,True])
    else: tt=tt.sort_index()
    available=cc.index.to_numpy(); cp=cc.pscore_6var.to_numpy(); rows=[]
    for pid,(ti,tr) in enumerate(tt.iterrows(),1):
        if len(cp)==0: break
        j=int(np.argmin(np.abs(cp-tr.pscore_6var))); ci=int(available[j])
        rows.append((pid,ti,ci,float(abs(cp[j]-tr.pscore_6var))))
        available=np.delete(available,j); cp=np.delete(cp,j)
    return rows

old_controls=set(d.loc[(d.old_match.eq(1))&(d.treated.eq(0)),'name_key'])
old_treated=set(d.loc[(d.old_match.eq(1))&(d.treated.eq(1)),'name_key'])
summary=[]; allpairs={}
for order in ['original','ascending','descending']:
    pairs=greedy(order); allpairs[order]=pairs
    nc=set(e.loc[[r[2] for r in pairs],'name_key']); nt=set(e.loc[[r[1] for r in pairs],'name_key'])
    summary.append({'treated_order':order,'matched_pairs':len(pairs),
                    'treated_overlap':len(old_treated&nt),'control_overlap':len(old_controls&nc),
                    'control_overlap_pct':100*len(old_controls&nc)/len(old_controls)})
s=pd.DataFrame(summary); s.to_csv(ROOT+r"\rematch_6var_overlap_summary.csv",index=False,encoding='utf-8-sig')
best=s.sort_values(['control_overlap','treated_order'],ascending=[False,True]).iloc[0].treated_order
pairs=allpairs[best]; e['new_match_6var']=0; e['pair_id_6var']=np.nan; e['match_distance_6var']=np.nan
for pid,ti,ci,dist in pairs:
    e.loc[[ti,ci],'new_match_6var']=1; e.loc[[ti,ci],'pair_id_6var']=pid; e.loc[[ti,ci],'match_distance_6var']=dist

out=d.merge(e[['name_key','pscore_6var','common_support_6var','new_match_6var','pair_id_6var','match_distance_6var']],on='name_key',how='left')
out['membership_status']=np.select([
    out.old_match.eq(1)&out.new_match_6var.eq(1),out.old_match.eq(1)&out.new_match_6var.ne(1),out.old_match.ne(1)&out.new_match_6var.eq(1)
],['both','old_only','new_only'],default='neither')
out.to_csv(ROOT+r"\rematch_6var_firm_comparison.csv",index=False,encoding='utf-8-sig')
stata=out.copy()
for c in stata.select_dtypes(include='object'): stata[c]=stata[c].where(stata[c].notna(),'').astype(str)
stata.to_stata(ROOT+r"\rematch_6var_full7316.dta",write_index=False,version=118)
stata.loc[stata.new_match_6var.eq(1)].to_stata(ROOT+r"\rematch_6var_matched_sample.dta",write_index=False,version=118)

print(s.to_string(index=False))
print('best order',best)
print('eligible',len(e),'treated',int(e.treated.sum()),'controls',int((e.treated==0).sum()))
print('support range',lo,hi)
print('on support treated',int(((e.treated==1)&(e.common_support_6var==1)).sum()),'controls',int(((e.treated==0)&(e.common_support_6var==1)).sum()))
print(out.membership_status.value_counts().to_string())
