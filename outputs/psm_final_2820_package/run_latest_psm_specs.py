from pathlib import Path
import re
import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\user\Documents\VD\outputs\psm_final_2820_package")
OUT = ROOT / "latest_code_caliper005"
OUT.mkdir(exist_ok=True)
V6 = Path(r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms\exact matched sample v6 unmatched.xlsx")
LEGACY = Path(r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms\240626.dta")
DEALS = Path(r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms\2010 2015 Crunchbase deals merged_v4.xlsx")

def key(x): return re.sub(r"[^a-z0-9]", "", str(x).casefold())

d = pd.read_excel(V6)
d["name_key"] = d["Organization Name"].map(key)
l = pd.read_stata(LEGACY, convert_categoricals=False)
l["name_key"] = l["OrganizationName"].map(key)
l = l.drop_duplicates("name_key")
lk = l[["name_key", "Patents_VD", "VD_Year", "ln_Total_Funding_Amount_T3"]].copy()
d = d.merge(lk, on="name_key", how="left", validate="many_to_one")

# The surviving 7,316-firm pre-match workbook stores the same pre-VD patent count as Grant_VD.
d["Patents_VD"] = d["Patents_VD"].fillna(d["Grant_VD"])
d["VD_Year"] = d["VD_Year"].fillna(d["VD Year"])
d["ln_Total_Funding_Amount_FirstVD"] = np.log1p(pd.to_numeric(d["Total_Funding_Amount_FirstVD"], errors="coerce"))

# Recover the T+3 outcome for the two firms absent from the 7,314-firm legacy file when available.
deals = pd.read_excel(DEALS, header=1)
firm = deals[deals["First VC"].eq(1)].copy()
firm["name_key"] = firm["Organization Name"].map(key)
firm["ln_t3_v4"] = np.log1p(pd.to_numeric(firm["Total_Funding_Amount_T3"], errors="coerce"))
firm = firm.drop_duplicates("name_key")
d = d.merge(firm[["name_key", "ln_t3_v4"]], on="name_key", how="left")
d["ln_Total_Funding_Amount_T3"] = d["ln_Total_Funding_Amount_T3"].fillna(d["ln_t3_v4"])

def score(frame, categorical, continuous):
    z = frame.dropna(subset=categorical + continuous).copy()
    C = pd.get_dummies(z[categorical].astype(str), drop_first=True, dtype=float)
    X = pd.concat([C, z[continuous].apply(pd.to_numeric, errors="coerce")], axis=1)
    X.insert(0, "const", 1.0)
    xv, yv = X.to_numpy(float), z["VD_Backing"].to_numpy(float)
    b = np.zeros(xv.shape[1])
    for _ in range(400):
        eta = np.clip(xv @ b, -30, 30)
        p = 1 / (1 + np.exp(-eta))
        w = np.clip(p * (1-p), 1e-9, None)
        zwork = eta + (yv-p)/w
        sw = np.sqrt(w)
        bn = np.linalg.pinv(xv * sw[:, None]) @ (zwork * sw)
        if np.max(np.abs(bn-b)) < 1e-10:
            b = bn; break
        b = bn
    z["pscore"] = 1 / (1 + np.exp(-np.clip(xv @ b, -30, 30)))
    return z

def match(z, label, caliper=.05):
    t, c = z[z.VD_Backing.eq(1)].copy(), z[z.VD_Backing.eq(0)].copy()
    lo, hi = max(t.pscore.min(), c.pscore.min()), min(t.pscore.max(), c.pscore.max())
    t["on_support"] = t.pscore.between(lo, hi)
    c["on_support"] = c.pscore.between(lo, hi)
    tt = t[t.on_support].sort_values(["pscore", "name_key"])
    cc = c[c.on_support].sort_values(["pscore", "name_key"])
    available = cc.index.to_numpy(); cp = cc.pscore.to_numpy(); rows=[]
    for _, tr in tt.iterrows():
        if not len(available): break
        j = int(np.argmin(np.abs(cp-tr.pscore)))
        dist = float(abs(cp[j]-tr.pscore))
        if dist <= caliper:
            rows.append((len(rows)+1, int(tr.name), int(available[j]), dist))
            available = np.delete(available, j); cp = np.delete(cp, j)
    pair_rows=[]
    for pid, ti, ci, dist in rows:
        tr, cr = z.loc[ti], z.loc[ci]
        pair_rows.append({
            "pair_id":pid,"treated_firm":tr["Organization Name"],"control_firm":cr["Organization Name"],
            "treated_pscore":tr.pscore,"control_pscore":cr.pscore,"absolute_distance":dist,
            "treated_outcome_ln_T3":tr.ln_Total_Funding_Amount_T3,
            "control_outcome_ln_T3":cr.ln_Total_Funding_Amount_T3,
            "pair_outcome_difference":tr.ln_Total_Funding_Amount_T3-cr.ln_Total_Funding_Amount_T3,
        })
    pairs=pd.DataFrame(pair_rows)
    pairs.to_csv(OUT/f"{label}_matched_pairs.csv",index=False,encoding="utf-8-sig")
    ids={i for r in rows for i in (r[1],r[2])}
    full=d.copy(); full["estimation_sample"]=full.index.isin(z.index).astype(int)
    full["pscore"]=np.nan; full.loc[z.index,"pscore"]=z.pscore
    full["matched"]=full.index.isin(ids).astype(int)
    full.to_csv(OUT/f"{label}_full7316.csv",index=False,encoding="utf-8-sig")
    complete=pairs.dropna(subset=["pair_outcome_difference"])
    return {
        "specification":label,"initial_firms":len(d),"estimation_sample":len(z),
        "eligible_treated":int(t.shape[0]),"eligible_controls":int(c.shape[0]),
        "support_lower":lo,"support_upper":hi,"treated_on_support":int(t.on_support.sum()),
        "controls_on_support":int(c.on_support.sum()),"matched_pairs":len(pairs),
        "matched_firms":2*len(pairs),"unmatched_treated_after_caliper":int(t.on_support.sum()-len(pairs)),
        "outcome_complete_pairs":len(complete),"ATT_ln_Total_Funding_Amount_T3":complete.pair_outcome_difference.mean(),
    }

# Exact psmatch2 covariate list supplied by the user; outcome() does not enter the score model.
s1 = score(d, ["Founding_Year", "Region2", "Industry2"], [
    "ln_Total_Funding_Amount_FirstVD", "NumberOfFunding_Rounds_FirstVD", "Patents_VD", "TimeToFirst_VC"
])

# Separate manual-logit recollection supplied by the user. This includes VD year and the funding amount in levels.
s2 = score(d, ["Industry2", "Region2"], [
    "Total_Funding_Amount_FirstVD", "NumberOfFunding_Rounds_FirstVD", "Patents_VD",
    "Founding_Year", "TimeToFirst_VC", "VD_Year"
])

summary=pd.DataFrame([match(s1,"spec_A_psmatch2_direct"),match(s2,"spec_B_manual_logit_with_VDYear")])
summary.to_csv(OUT/"specification_comparison.csv",index=False,encoding="utf-8-sig")
print(summary.to_string(index=False))
