from pathlib import Path
import pandas as pd

root=Path(r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms")
for name in ["250925.dta","250929.dta","251003.dta","260122 winsorization.dta","251111 2820 cross sectional.dta"]:
    p=root/name
    d=pd.read_stata(p,convert_categoricals=False)
    print("\nFILE",name,"shape",d.shape)
    targets=[c for c in d.columns if any(k in c.lower() for k in ["organization","patentbyfiling_win3","fwd_norm_cohort_win3","moneyraised_win","acq3","public3","badexit3","vdyear","founding","industry2","region2"])]
    print(targets)
    for c in targets:
        if c in d.columns:
            print(c,"nonmissing",int(d[c].notna().sum()),"unique",int(d[c].nunique(dropna=True)))
