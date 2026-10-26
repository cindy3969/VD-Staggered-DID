"""Supporting financing outcomes; never overwrite the master cross-section.

Calendar-year reference (Dec 31 of VDyear), not the exact VD closing date.
2023 cutoff is a conservative working assumption: raw data end 2023-12-26.
User recalls complete collection through end-2024; this discrepancy remains.
"""
from pathlib import Path
import json
import re
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "outputs/psm_final_2820_package"
OUT = ROOT / "outputs/downstream_financing"
OUT.mkdir(exist_ok=True)
CUTOFF = pd.Timestamp("2023-12-31")  # Change only after source coverage verification.
SOURCE = Path("C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms/2010 2015 Crunchbase deals merged_v4.xlsx")
d = pd.read_stata(PKG / "table3_original_2820_cross_section_v2.dta", convert_categoricals=False)
cols = ["firm_id", "OrganizationName", "VD", "VDyear", "patentdummybyfiling",
        "earlystage", "ln_MoneyRaised_VD", "NumofFundingRounds_VD", "Region2",
        "Industry2", "Foundingyear"]
d = d[cols].copy()
key = lambda x: re.sub("[^a-z0-9]", "", str(x).lower())
d["key"] = d.OrganizationName.map(key)
assert d.key.is_unique and d.firm_id.is_unique
r = pd.read_excel(SOURCE, header=1, usecols=["Organization Name", "deal no",
    "Announced Date", "Deal year", "Funding Type", "Money Raised Currency (in USD)"])
r["key"] = r["Organization Name"].map(key)
assert d.key.isin(r.key).all()
r = r[r.key.isin(d.key)].copy()
assert not r.duplicated(["key", "deal no"]).any()
r["date"] = pd.to_datetime(r["Announced Date"], errors="coerce")
assert r.date.notna().all(), "Unknown dates require explicit handling."
date_year_mismatches = r.loc[~r.date.dt.year.eq(r["Deal year"])].copy()
date_year_mismatches.to_csv(OUT / "deal_year_date_discrepancies.csv", index=False)
# Use the announced date consistently; do not mix date and derived Deal year.
r["amount"] = pd.to_numeric(r["Money Raised Currency (in USD)"], errors="coerce")
assert r.amount.dropna().ge(0).all()
t = r["Funding Type"].fillna("").str.strip()
# Primary private equity; exclude debt, convertible notes, secondary transactions,
# post-IPO equity and ambiguous Funding Round.
r["equity"] = t.isin(["Seed", "Pre-Seed", "Angel", "Venture - Series Unknown",
    "Private Equity", "Corporate Round", "Equity Crowdfunding"]) | t.str.match(r"^Series [A-I](?:\d+)?$")
d["reference"] = pd.to_datetime(d.VDyear.astype(int).astype(str) + "-12-31")
w = r.merge(d[["firm_id", "key", "reference"]], on="key", validate="many_to_one")
w = w[w.equity & w.date.gt(w.reference) & w.date.le(CUTOFF)].copy()
w.sort_values(["firm_id", "date", "deal no"], inplace=True)
# First date can contain multiple distinct rounds. Report total on that date;
# exclude tied dates from the conditional single-round amount regression.
firstdate = w.groupby("firm_id").date.min()
first = w[w.date.eq(w.firm_id.map(firstdate))]
a = first.groupby("firm_id").agg(next_date=("date", "min"), next_n=("date", "size"),
    next_disclosed=("amount", "count"), next_amount=("amount", "sum"))
a.loc[a.next_disclosed.ne(a.next_n), "next_amount"] = np.nan
d = d.merge(a, on="firm_id", how="left", validate="one_to_one")
d["observed"] = d.reference.lt(CUTOFF).astype("int8")
d["next_event"] = d.next_date.notna().astype("int8")
d["followup_days"] = (CUTOFF - d.reference).dt.days
d["next_days"] = (d.next_date - d.reference).dt.days
d["duration_days"] = d.next_days.fillna(d.followup_days)
d.loc[d.observed.eq(0), ["next_event", "duration_days"]] = np.nan
for h in (1, 2, 3):
    end = pd.to_datetime((d.VDyear.astype(int) + h).astype(str) + "-12-31")
    complete = end.le(CUTOFF) & d.observed.eq(1)
    wh = w[w.date.le(w.firm_id.map(pd.Series(end.values, index=d.firm_id)))]
    agg = wh.groupby("firm_id").agg(n=("amount", "size"), known=("amount", "count"), total=("amount", "sum"))
    n = d.firm_id.map(agg.n).fillna(0)
    missing_amount = d.firm_id.map(agg.n - agg.known).fillna(0).gt(0)
    d[f"complete{h}"] = complete.astype("int8")
    d[f"raise{h}"] = n.gt(0).astype(float).where(complete)
    d[f"cum{h}"] = d.firm_id.map(agg.total).fillna(0).where(complete & ~missing_amount)
    d[f"undisclosed{h}"] = missing_amount.astype(float).where(complete)
    assert d.loc[complete & n.eq(0), f"cum{h}"].eq(0).all()
    assert d.loc[~complete | missing_amount, f"cum{h}"].isna().all()
w.to_csv(OUT / "eligible_deals.csv", index=False, encoding="utf-8-sig")
report = {"cutoff_assumption": str(CUTOFF.date()),
    "date_year_discrepancies_using_announced_date": len(date_year_mismatches),
    "raw_max_date": str(r.date.max().date()), "N": len(d),
    "reference": "December 31 of VD/reference year; excludes same-year rounds",
    "caveat": "2024 recalled collection cutoff is not supported by dates in this source. 2023 completeness remains a working assumption. No competing-exit adjustment.",
    "next_events": int(d.next_event.sum()),
    "first_date_multiple_rounds": int(d.next_n.gt(1).sum()),
    "horizons": {h: {"complete": int(d[f"complete{h}"].sum()),
        "raised": int(d[f"raise{h}"].sum()), "genuine_zeros_assuming_coverage": int(d[f"cum{h}"].eq(0).sum()),
        "undisclosed": int(d[f"undisclosed{h}"].sum())} for h in (1, 2, 3)}}
(OUT / "construction_audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
d.drop(columns=["key", "reference", "next_date"]).to_stata(OUT / "financing_support.dta", write_index=False, version=118)
print(json.dumps(report, indent=2))
