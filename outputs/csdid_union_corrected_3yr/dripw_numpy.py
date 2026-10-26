import pandas as pd, numpy as np, warnings, sys
warnings.filterwarnings('ignore')
P=pd.read_csv('hist_panel.csv',low_memory=False)
XV=['ln1p_cum_funding_l1','cum_funding_rounds_l1']
def logit(X,d,w):
    b=np.zeros(X.shape[1])
    eye=np.eye(X.shape[1])
    for _ in range(60):
        z=np.clip(X@b,-30,30); pr=1/(1+np.exp(-z))
        grad=X.T@(w*(d-pr))-2e-6*b
        hess=X.T@((w*pr*(1-pr))[:,None]*X)+2e-6*eye
        step=np.linalg.lstsq(hess,grad,rcond=None)[0]
        b=b+step
        if np.max(np.abs(step))<1e-8: break
    return 1/(1+np.exp(-(X@b)))
def prep(p,y,ly):
    Y=p.pivot(index='full_firm_id',columns='year',values=y).reindex(columns=range(2010,ly+1))
    ids=Y.index
    Xs={v:p.pivot(index='full_firm_id',columns='year',values=v).reindex(index=ids,columns=range(2010,ly+1)).values for v in XV}
    f=p.drop_duplicates('full_firm_id').set_index('full_firm_id').reindex(ids)
    D=pd.get_dummies(f.region_fe.astype(int),prefix='r',drop_first=True).join(pd.get_dummies(f.industry_fe.astype(int),prefix='i',drop_first=True)).values.astype(float)
    return Y.values,Xs,D,f.G.values,ids
def att_cells(Yv,Xs,D,G,w,ly,ctrl,cov=True):
    res={}
    for g in sorted(set(G[G>0])):
        for t in range(2011,ly+1):
            b=g-1 if t>=g else t-1
            if b<2010: continue
            tr=G==g; c=(G==0) if ctrl=='never' else ((G==0)|(G>max(t,b)))
            m=(tr|c)&~np.isnan(Yv[:,t-2010])&~np.isnan(Yv[:,b-2010])&(w>0)
            if cov:
                X=np.column_stack([np.ones(len(G)),Xs[XV[0]][:,b-2010],Xs[XV[1]][:,b-2010],D])
                m&=~np.isnan(X).any(1)
            dd=tr[m].astype(float); 
            if dd.sum()==0 or (1-dd).sum()<5: continue
            dy=Yv[m,t-2010]-Yv[m,b-2010]; ww=w[m]
            if not cov:
                a=(ww*dd*dy).sum()/(ww*dd).sum()-(ww*(1-dd)*dy).sum()/(ww*(1-dd)).sum()
            else:
                Xm=X[m]; Xm[:,1:3]=(Xm[:,1:3]-Xm[:,1:3].mean(0))/(Xm[:,1:3].std(0)+1e-9)
                ps=np.clip(logit(Xm,dd,ww),1e-6,1-1e-6)
                cw=ww*(1-dd); beta=np.linalg.lstsq(Xm*np.sqrt(cw)[:,None],dy*np.sqrt(cw),rcond=None)[0]
                r=dy-Xm@beta
                w1=ww*dd; w0=ww*(1-dd)*ps/(1-ps)
                a=(w1*r).sum()/w1.sum()-(w0*r).sum()/w0.sum()
            res[(g,t)]=(a,(w*tr).sum())
    return res
def agg(res,emin=-4,emax=4):
    post=[(k,v) for k,v in res.items() if k[1]>=k[0]]
    wt=np.array([v[1] for k,v in post]); a=np.array([v[0] for k,v in post]); simple=(wt*a).sum()/wt.sum()
    ev={}
    for e in range(emin,emax+1):
        cells=[v for k,v in res.items() if k[1]-k[0]==e]
        if cells: ev[e]=sum(x*w for x,w in cells)/sum(w for x,w in cells)
    return simple,ev,np.mean([ev[e] for e in range(0,emax+1)])
def estimate(sub,y,ctrl='never',ly=2024,cov=True,B=0,seed=1):
    p=P.copy()
    if sub=='noprior': p=p[(p.G==0)|(p.prior==0)]
    if sub=='prior': p=p[(p.G==0)|(p.prior==1)]
    if sub=='early': p=p[(p.G==0)|(p.early==1)]
    if sub=='late': p=p[(p.G==0)|(p.early==0)]
    Yv,Xs,D,G,ids=prep(p,y,ly)
    s,ev,pa=agg(att_cells(Yv,Xs,D,G,np.ones(len(G)),ly,ctrl,cov))
    out=dict(sub=sub,y=y,ctrl=ctrl,cov=cov,simple=s,post_avg=pa,obs=len(p),firms=p.full_firm_id.nunique(),**{f'e{e}':v for e,v in ev.items()})
    if B:
        rng=np.random.default_rng(seed); bs=[]
        for _ in range(B):
            w=rng.multinomial(len(G),np.ones(len(G))/len(G)).astype(float)
            s_,ev_,pa_=agg(att_cells(Yv,Xs,D,G,w,ly,ctrl,cov)); bs.append([s_,pa_]+[ev_.get(e,np.nan) for e in range(-4,5)])
        bs=np.array(bs); se=bs.std(0)
        out['simple_se'],out['post_avg_se']=se[0],se[1]
        for i,e in enumerate(range(-4,5)): out[f'se{e}']=se[i+2]
    return out
if __name__=='__main__':
    import json
    jobs=json.loads(sys.argv[1]); rows=[]
    for j in jobs:
        r=estimate(*j); rows.append(r); print({k:(round(v,3) if isinstance(v,float) else v) for k,v in r.items()},flush=True)
    pd.DataFrame(rows).to_csv(sys.argv[2],index=False)
