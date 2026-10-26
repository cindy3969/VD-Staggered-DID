from pathlib import Path
import re
import numpy as np
import pandas as pd

root=Path(r"C:\Users\user\Documents\VD\outputs\csdid_replicated_from_rebuilt_patent_list")
d=pd.read_stata(root/"csdid_rebuilt_patent_panel.dta",convert_categoricals=False)
d=d[~((d.g_first_vd>0)&(d.g_first_vd<=d.founding_year))].copy()

# Cohort-aligned raw means, weighted by treated cohort-year cell size.
cells=[]
for g in sorted(d.loc[d.g_first_vd>0,"g_first_vd"].unique()):
    for k in range(-4,5):
        yr=int(g+k)
        t=d[(d.g_first_vd==g)&(d.year==yr)]
        if t.empty: continue
        for comp,mask in {
            "Never treated":(d.g_first_vd==0)&(d.year==yr),
            "Not-yet treated":((d.g_first_vd==0)|(d.g_first_vd>yr+1))&(d.year==yr),
        }.items():
            c=d[mask]
            if len(c):
                cells += [(k,comp,"VD-backed",t.apps_ult_granted.mean(),len(t)),
                          (k,comp,"Control",c.apps_ult_granted.mean(),len(t))]
c=pd.DataFrame(cells,columns=["event_time","comparison","group","mean","w"])
agg=(c.groupby(["event_time","comparison","group"])
     .apply(lambda x:np.average(x["mean"],weights=x["w"]),include_groups=False)
     .rename("mean").reset_index())
agg.to_csv(root/"Figure_1a_raw_trajectories_data.csv",index=False)


# Parse all-firm event-study estimates from the completed Stata log.
txt=(root/"replicate_table1_and_figures.log").read_text(encoding="utf-8",errors="replace")
b=re.search(r"=== BEGIN_SPEC all OBS_RAW=.*?ATT by Periods Before and After treatment(.*?)=== END_SPEC all ===",txt,re.S).group(1)
pat=re.compile(r"^\s*(Tm[2-5]|Tp[0-4])\s*\|\s*([-+.0-9eE]+)\s+([-+.0-9eE]+)\s+[-+.0-9eE]+\s+([0-9.]+)\s+([-+.0-9eE]+)\s+([-+.0-9eE]+)",re.M)
mp={"Tm5":-4,"Tm4":-3,"Tm3":-2,"Tm2":-1,"Tp0":0,"Tp1":1,"Tp2":2,"Tp3":3,"Tp4":4}
ev=pd.DataFrame([(mp[a],float(v),float(se),float(p),float(lo),float(hi)) for a,v,se,p,lo,hi in pat.findall(b)],columns=["event_time","estimate","std_error","p_value","conf_low","conf_high"]).sort_values("event_time")
ev.to_csv(root/"Figure_1b_dynamic_ATT_data.csv",index=False)
print(agg.to_string(index=False)); print(ev.to_string(index=False))
