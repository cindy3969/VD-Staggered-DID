import pandas as pd

p = r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms\2010 2015 Crunchbase deals merged_v4.xlsx"
d = pd.read_excel(p, header=1)
print("shape", d.shape)
print("columns", list(enumerate(d.columns)))
print("unique URL", d["Organization Name URL"].nunique(), "unique name", d["Organization Name"].nunique())
print("weight cols", [c for c in d.columns if str(c).lower().startswith("weight")])
print("VD backing", d["VD_Backing"].value_counts(dropna=False).to_dict())
print("last deal", d["last deal"].value_counts(dropna=False).head().to_dict())
print("first VC", d["First VC"].value_counts(dropna=False).head().to_dict())
print("weights1", [(c, d[c].value_counts(dropna=False).head(10).to_dict()) for c in d.columns if str(c).lower().startswith("weight")])
f = d[d["First VC"].eq(1)].copy()
print("firm rows", f.shape)
print("firm VD", f["VD_Backing"].value_counts(dropna=False).to_dict())
print("firm weight", f["weight"].value_counts(dropna=False).to_dict())
print("firm weight x VD", pd.crosstab(f["VD_Backing"], f["weight"], dropna=False).to_string())
for c in ["TotalFundingAmount_FirstVD", "NumberOfFunding_Rounds_FirstVD", "TimeToFirst_VC", "found year", "Region", "Industry Classification", "Industry Groups", "Industries"]:
    print("VAR", c, "nonmissing", int(f[c].notna().sum()), "unique", int(f[c].nunique(dropna=True)))
    print(f[c].value_counts(dropna=False).head(10).to_dict())
print("possible patent cols", [c for c in d.columns if "pat" in str(c).lower() or "grant" in str(c).lower()])
