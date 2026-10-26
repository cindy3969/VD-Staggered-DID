from pathlib import Path
import numpy as np
import pandas as pd
from html import escape

ROOT = Path(r"C:\Users\user\Documents\VD\outputs\psm_final_2820_package")
SRC = ROOT / "psm_reestimated_membership_comparison.csv"
OUT = ROOT / "manuscript_7var_rematch"
OUT.mkdir(exist_ok=True)

d = pd.read_csv(SRC)
e = d[d["estimation_sample"].eq(1)].copy()
m = e[e["new_weight"].eq(1)].copy()

treated = m[m["VD_Backing"].eq(1)].copy()
controls = m[m["VD_Backing"].eq(0)].copy()

pair_cols = [
    "pair_id", "Organization Name", "Organization Name URL", "pscore_reestimated",
    "Founding_Year", "Region2", "Industry2", "TimeToFirst_VC",
    "NumberOfFunding_Rounds_FirstVD", "Total_Funding_Amount_FirstVD", "Grant_VD",
    "old_weight",
]
t = treated[pair_cols].rename(columns={c: f"treated_{c}" for c in pair_cols if c != "pair_id"})
c = controls[pair_cols].rename(columns={c: f"control_{c}" for c in pair_cols if c != "pair_id"})
pairs = t.merge(c, on="pair_id", how="inner", validate="one_to_one")
pairs["absolute_pscore_distance"] = (
    pairs["treated_pscore_reestimated"] - pairs["control_pscore_reestimated"]
).abs()
pairs = pairs.sort_values("pair_id")
pairs.to_csv(OUT / "matched_pairs_1410.csv", index=False, encoding="utf-8-sig")

firm_cols = [
    "pair_id", "matched_role", "Organization Name", "Organization Name URL", "VD_Backing",
    "pscore_reestimated", "common_support", "Founding_Year", "Region2", "Industry2",
    "TimeToFirst_VC", "NumberOfFunding_Rounds_FirstVD", "Total_Funding_Amount_FirstVD",
    "ln_Total_Funding_Amount_FirstVD", "Grant_VD", "old_weight",
]
m[firm_cols].sort_values(["pair_id", "VD_Backing"], ascending=[True, False]).to_csv(
    OUT / "matched_firms_2820.csv", index=False, encoding="utf-8-sig"
)

def smd_cont(x1, x0):
    x1, x0 = pd.to_numeric(x1, errors="coerce").dropna(), pd.to_numeric(x0, errors="coerce").dropna()
    den = np.sqrt((x1.var(ddof=1) + x0.var(ddof=1)) / 2)
    return np.nan if den == 0 else (x1.mean() - x0.mean()) / den

def vr(x1, x0):
    v1, v0 = pd.to_numeric(x1, errors="coerce").var(ddof=1), pd.to_numeric(x0, errors="coerce").var(ddof=1)
    return np.nan if v0 == 0 else v1 / v0

def smd_binary(x1, x0):
    p1, p0 = x1.mean(), x0.mean()
    den = np.sqrt((p1 * (1-p1) + p0 * (1-p0)) / 2)
    return 0.0 if den == 0 and p1 == p0 else ((p1-p0)/den if den else np.nan)

rows = []
continuous = {
    "Log(Total Funding Amount_VD)": "ln_Total_Funding_Amount_FirstVD",
    "Number Of Funding Rounds_VD": "NumberOfFunding_Rounds_FirstVD",
    "Pre Granted Patent Applications_VD": "Grant_VD",
    "Time to First VC": "TimeToFirst_VC",
}
for label, col in continuous.items():
    eb1, eb0 = e.loc[e.VD_Backing.eq(1), col], e.loc[e.VD_Backing.eq(0), col]
    ma1, ma0 = m.loc[m.VD_Backing.eq(1), col], m.loc[m.VD_Backing.eq(0), col]
    rows.append({"covariate": label, "type": "continuous", "matched_on": "Yes",
                 "smd_before": smd_cont(eb1, eb0), "smd_after": smd_cont(ma1, ma0),
                 "variance_ratio_before": vr(eb1, eb0), "variance_ratio_after": vr(ma1, ma0),
                 "treated_mean_before": eb1.mean(), "control_mean_before": eb0.mean(),
                 "treated_mean_after": ma1.mean(), "control_mean_after": ma0.mean()})

for col, label in [("Founding_Year", "Founding Year"), ("Region2", "Region"), ("Industry2", "Industry")]:
    levels = sorted(e[col].dropna().unique(), key=lambda z: str(z))
    for level in levels:
        eb1 = (e.loc[e.VD_Backing.eq(1), col] == level).astype(float)
        eb0 = (e.loc[e.VD_Backing.eq(0), col] == level).astype(float)
        ma1 = (m.loc[m.VD_Backing.eq(1), col] == level).astype(float)
        ma0 = (m.loc[m.VD_Backing.eq(0), col] == level).astype(float)
        rows.append({"covariate": f"{label}: {level}", "type": "categorical level", "matched_on": "Yes",
                     "smd_before": smd_binary(eb1, eb0), "smd_after": smd_binary(ma1, ma0),
                     "variance_ratio_before": np.nan, "variance_ratio_after": np.nan,
                     "treated_mean_before": eb1.mean(), "control_mean_before": eb0.mean(),
                     "treated_mean_after": ma1.mean(), "control_mean_after": ma0.mean()})

bal = pd.DataFrame(rows)
bal["abs_smd_before"] = bal.smd_before.abs()
bal["abs_smd_after"] = bal.smd_after.abs()
bal.to_csv(OUT / "balance_diagnostics.csv", index=False, encoding="utf-8-sig")

tb = e[e.VD_Backing.eq(1)].pscore_reestimated
cb = e[e.VD_Backing.eq(0)].pscore_reestimated
lo, hi = max(tb.min(), cb.min()), min(tb.max(), cb.max())
summary = pd.DataFrame([
    ["Initial firms", len(d)],
    ["Eligible firms (complete matching covariates)", len(e)],
    ["Eligible VD-backed firms", int(e.VD_Backing.sum())],
    ["Eligible VC-only firms", int((e.VD_Backing == 0).sum())],
    ["Common-support lower bound", lo],
    ["Common-support upper bound", hi],
    ["VD-backed firms on support", int(((e.VD_Backing == 1) & (e.common_support == 1)).sum())],
    ["VC-only firms on support", int(((e.VD_Backing == 0) & (e.common_support == 1)).sum())],
    ["VD-backed firms off support", int(((e.VD_Backing == 1) & (e.common_support == 0)).sum())],
    ["VC-only firms off support", int(((e.VD_Backing == 0) & (e.common_support == 0)).sum())],
    ["Matched VD-backed firms", len(treated)],
    ["Matched VC-only firms", len(controls)],
    ["Maximum absolute SMD before", bal.abs_smd_before.max()],
    ["Maximum absolute SMD after", bal.abs_smd_after.max()],
    ["Rows with absolute SMD > 0.10 after", int((bal.abs_smd_after > .10).sum())],
    ["Median absolute propensity-score distance", pairs.absolute_pscore_distance.median()],
    ["Maximum absolute propensity-score distance", pairs.absolute_pscore_distance.max()],
], columns=["statistic", "value"])
summary.to_csv(OUT / "common_support_and_summary.csv", index=False, encoding="utf-8-sig")

plot = bal.sort_values("abs_smd_before").reset_index(drop=True)
width, left, right, top, row_h = 1200, 430, 50, 80, 24
height = top + row_h * len(plot) + 80
xmax = max(.40, float(plot[["abs_smd_before", "abs_smd_after"]].max().max()) * 1.08)
def xpos(v): return left + float(v) / xmax * (width-left-right)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
       '<rect width="100%" height="100%" fill="white"/>',
       '<style>text{font-family:Arial,sans-serif;fill:#222}.lab{font-size:12px}.tick{font-size:11px}.title{font-size:18px;font-weight:700}</style>',
       f'<text x="{width/2}" y="28" text-anchor="middle" class="title">Love plot: 1:1 propensity-score matching</text>']
for tick in np.arange(0, xmax + .0001, .05):
    x = xpos(tick)
    svg.append(f'<line x1="{x:.1f}" y1="50" x2="{x:.1f}" y2="{height-50}" stroke="#e5e5e5"/>')
    svg.append(f'<text x="{x:.1f}" y="{height-28}" text-anchor="middle" class="tick">{tick:.2f}</text>')
x10 = xpos(.10)
svg.append(f'<line x1="{x10:.1f}" y1="50" x2="{x10:.1f}" y2="{height-50}" stroke="#666" stroke-dasharray="6 5" stroke-width="1.5"/>')
for i, r in plot.iterrows():
    y = top + i * row_h
    svg.append(f'<text x="{left-12}" y="{y+4}" text-anchor="end" class="lab">{escape(str(r.covariate))}</text>')
    svg.append(f'<circle cx="{xpos(r.abs_smd_before):.1f}" cy="{y-4}" r="4" fill="#9C2F2F"/>')
    svg.append(f'<circle cx="{xpos(r.abs_smd_after):.1f}" cy="{y+5}" r="4" fill="#22577A"/>')
svg.append(f'<circle cx="{left}" cy="50" r="4" fill="#9C2F2F"/><text x="{left+10}" y="54" class="tick">Before matching</text>')
svg.append(f'<circle cx="{left+135}" cy="50" r="4" fill="#22577A"/><text x="{left+145}" y="54" class="tick">After matching</text>')
svg.append(f'<text x="{(left+width-right)/2}" y="{height-6}" text-anchor="middle" class="lab">Absolute standardized mean difference</text></svg>')
(OUT / "love_plot_7var.svg").write_text("\n".join(svg), encoding="utf-8")

print(summary.to_string(index=False))
print("pairs", len(pairs), "firms", len(m))
