import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
p=pd.read_csv('hist_panel.csv',low_memory=False); y='ultimately_granted_filings'
tr=p[p.G>0].copy(); tr['e']=tr.year-tr.G; tr=tr[tr.e.between(-4,4)]
T=tr.groupby('e')[y].mean()
ym=p[p.G==0].groupby('year')[y].mean()
w=tr.groupby(['e','G']).size().rename('n').reset_index(); w['cm']=(w.G+w.e).map(ym)
C=w.groupby('e').apply(lambda d:(d.n*d.cm).sum()/d.n.sum(),include_groups=False)
r=pd.read_csv('bt_0.csv').iloc[0]; E=list(range(-4,5))
b=np.array([r[f'e{e}'] for e in E]); s=np.array([r[f'se{e}'] for e in E])
cf={-1:T[-1]}; cf.update({e:T[e]-r[f'e{e}'] for e in range(0,5)})
pd.DataFrame({'treated_mean':T,'control_mean':C,'counterfactual':pd.Series(cf),'att':b,'se':s},index=E).round(4).to_csv('/home/claude/figure1_data.csv')
RED,NAVY='#c0002f','#1f3d63'
fig,axs=plt.subplots(1,2,figsize=(13,4.8))
ax=axs[0]
ax.plot(E,T.values,'-o',color=RED,lw=1.6,ms=7,label='Treated (VD-backed)')
ax.plot(E,C.values,'-s',color=NAVY,lw=1.6,ms=6,label='Control (never treated)')
ax.plot(list(cf.keys()),list(cf.values()),'--',color=RED,lw=1.6,label='Counterfactual (treated − ATT)')
ax.vlines(3,T[3],cf[3],color=RED,lw=1.3); ax.text(3.08,(T[3]+cf[3])/2,f'ATT(t=3) = {r["e3"]:.3f}',fontsize=9)
ax.axvline(0,color='#666',ls='--',lw=1.2); ax.set_xticks(E); ax.set_xlabel('Time'); ax.set_ylabel('Mean ultimately granted applications per firm-year')
ax.set_title('Panel A. Observed and counterfactual trajectories',loc='left',fontsize=10.5); ax.legend(frameon=False,fontsize=8.5,loc='lower left')
ax=axs[1]
ax.errorbar(E,b,yerr=1.96*s,fmt='-o',color=NAVY,ecolor=NAVY,capsize=3,lw=1.5,ms=6,mfc='black',mec='black')
ax.axhline(0,color='#888',lw=1); ax.axvline(0,color='#666',ls='--',lw=1.2); ax.set_xticks(E); ax.set_xlabel('Time'); ax.set_ylabel('ATT (count)')
ax.set_title("Panel B. Callaway–Sant'Anna event-study estimates",loc='left',fontsize=10.5)
for a in axs:
    a.grid(color='#eeeeea',ls='--'); [a.spines[k].set_visible(False) for k in ['top','right']]
fig.text(0.01,0.01,'Replication: full panel through 2024 (88,547 firm-years, 7,273 firms); never-treated controls; DR estimator with lagged funding, lagged rounds, region and industry FE; 95% CI from firm bootstrap (49 reps).',fontsize=7.5,color='#555')
plt.tight_layout(rect=[0,0.04,1,1]); plt.savefig('/home/claude/Figure1_replication.png',dpi=200)
