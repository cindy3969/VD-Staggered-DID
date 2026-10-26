import os, re, json
import pandas as pd

roots=[r'C:\Users\user\Documents',r'C:\Users\user\iCloudDrive',r'C:\Users\user\OneDrive',r'C:\Users\user\Desktop',r'C:\Users\user\Downloads']
rows=[]
for root in roots:
    if not os.path.exists(root): continue
    for dp,dns,fns in os.walk(root):
        dns[:]=[x for x in dns if x.lower() not in {'node_modules','.git','appdata'}]
        for fn in fns:
            p=os.path.join(dp,fn); ext=os.path.splitext(fn)[1].lower()
            if ext=='.dta':
                try:
                    d=pd.read_stata(p,convert_categoricals=False)
                    hits=[c for c in d.columns if re.search(r'patent|application|grant|citation|fwd|event_time|g_first_vd|apps_',c,re.I)]
                    rows.append({'path':p,'ext':ext,'n':len(d),'k':len(d.columns),'hits':'|'.join(hits),'size':os.path.getsize(p)})
                except Exception as e: rows.append({'path':p,'ext':ext,'error':str(e),'size':os.path.getsize(p)})
            elif ext in {'.csv','.parquet','.feather'} and (os.path.getsize(p)>100_000 or re.search(r'patent|application|citation|panel|7316|full',fn,re.I)):
                try:
                    if ext=='.csv': d=pd.read_csv(p,nrows=5)
                    elif ext=='.parquet': d=pd.read_parquet(p)
                    else: d=pd.read_feather(p)
                    hits=[c for c in d.columns if re.search(r'patent|application|grant|citation|fwd|event_time|g_first_vd|apps_',c,re.I)]
                    if hits or re.search(r'patent|application|citation|panel|7316|full',fn,re.I): rows.append({'path':p,'ext':ext,'n':'','k':len(d.columns),'hits':'|'.join(hits),'size':os.path.getsize(p)})
                except Exception: pass
out=pd.DataFrame(rows)
out.to_csv(r'C:\Users\user\Documents\VD\outputs\psm_final_2820_package\all_user_datafile_scan.csv',index=False,encoding='utf-8-sig')
print(out.to_string(index=False))
