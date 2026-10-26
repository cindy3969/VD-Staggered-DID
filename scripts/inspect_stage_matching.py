import re
import pandas as pd

def norm(s): return re.sub(r"[^a-z0-9]", "", str(s).lower())

f = pd.read_stata(r"outputs/csdid_ultimately_granted_primary/csdid_ultimately_granted_full7316_controls.dta", convert_categoricals=False)
f = f[(f.g_first_vd > f.founding_year) & (f.g_first_vd > 0)].copy()
f["key"] = f.organization_name.map(norm)
x = pd.read_excel(r"C:\Users\user\OneDrive\바탕 화면\2010 2015 Crunchbase deals merged_v4.xlsx", header=1)
x["key"] = x["Organization Name"].map(norm)
first = x.sort_values(["key", "deal no"]).drop_duplicates("key")
vdrow = x[pd.to_numeric(x["First VD.1"], errors="coerce").eq(1)].sort_values(["key", "Announced Date"]).drop_duplicates("key")
for label,d in [("first",first),("vdrow",vdrow)]:
    m=f.merge(d[["key","Funding Status","Funding Stage","Funding Type"]],on="key",how="left")
    print("\n",label,"matched",m["Funding Status"].notna().sum(),"of",len(m))
    print(m["Funding Status"].value_counts(dropna=False).to_string())

x["date"] = pd.to_datetime(x["Announced Date"], errors="coerce")
x["is_debt"] = x["Funding Type"].astype(str).str.contains("Debt", case=False, na=False)
vd_dates = vdrow.assign(date=pd.to_datetime(vdrow["Announced Date"], errors="coerce")).set_index("key")["date"].to_dict()
records=[]
for key,g in x.groupby("key"):
    vd=vd_dates.get(key)
    if pd.isna(vd): continue
    e=g[(g.date<=vd)&~g.is_debt].sort_values("date")
    r=e.iloc[-1] if len(e) else None
    records.append({"key":key,"prior_stage":None if r is None else r["Funding Stage"],"prior_type":None if r is None else r["Funding Type"]})
p=pd.DataFrame(records)
m=f.merge(p,on="key",how="left")
print("\nPrior equity stage/type")
print(m.prior_stage.value_counts(dropna=False).to_string())
print(m.prior_type.value_counts(dropna=False).head(30).to_string())
