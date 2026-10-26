import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from openpyxl import load_workbook

PANEL = r"C:\Users\user\Documents\VD\2010 2015 Crunchbase deals merged_v4_series-updated.xlsx"
KEYS = r"C:\Users\user\Documents\VD\.artifact_work\dta_keys.csv"
OUT = r"C:\Users\user\Documents\VD\.artifact_work\stage_crosswalk.csv"
SUMMARY = r"C:\Users\user\Documents\VD\.artifact_work\stage_crosswalk_summary.json"

ORD = {"Pre-Seed": -1, "Seed": 0}
ORD.update({f"Series {chr(65+i)}": i+1 for i in range(26)})

with open(KEYS, encoding="utf-8-sig", newline="") as f:
    keys = list(csv.DictReader(f))
key_by_name = {r["OrganizationName"]: r for r in keys}

wb = load_workbook(PANEL, read_only=True, data_only=True)
ws = wb.active
panel = defaultdict(list)
for x in ws.iter_rows(min_row=3, values_only=True):
    if x[36] != 1:
        continue
    panel[x[3]].append({
        "date": x[7], "year": x[8], "funding_type": x[11],
        "vd_backing": x[16], "first_vd": x[17], "reference_year": x[31]
    })

out = []
unmatched = []
missing_stage = []
for name, key in key_by_name.items():
    rows = panel.get(name)
    if not rows:
        unmatched.append(name)
        continue
    vd = int(float(key["VD"]))
    ref_year = int(float(key["VDyear"]))
    first_vd_dates = [r["date"] for r in rows if r["first_vd"] == 1 and isinstance(r["date"], datetime)]
    cutoff = min(first_vd_dates) if vd == 1 and first_vd_dates else datetime(ref_year, 12, 31)
    eligible = [(ORD[r["funding_type"]], r["funding_type"], r["date"]) for r in rows
                if r["funding_type"] in ORD and isinstance(r["date"], datetime) and r["date"] <= cutoff]
    method = "carried forward highest observed series"
    if eligible:
        max_ord, max_stage, _ = max(eligible, key=lambda z: (z[0], z[2]))
    else:
        future = sorted([(ORD[r["funding_type"]], r["funding_type"], r["date"]) for r in rows
                         if r["funding_type"] in ORD and isinstance(r["date"], datetime) and r["date"] > cutoff],
                        key=lambda z: z[2])
        if future:
            next_ord, next_label, _ = future[0]
            max_ord = max(0, next_ord - 1)
            max_stage = label_for(max_ord) if 'label_for' in globals() else ("Seed" if max_ord == 0 else f"Series {chr(64+max_ord)}")
            method = "backcast one stage from first subsequent observed series"
        else:
            venture_types = {"Angel", "Convertible Note", "Equity Crowdfunding", "Corporate Round", "Private Equity", "Funding Round", "Secondary Market"}
            qualifying = sorted([r for r in rows if isinstance(r["date"], datetime) and r["date"] <= cutoff and r["funding_type"] in venture_types], key=lambda r:r["date"])
            if qualifying:
                max_ord = max(0, len(qualifying)-1)
                max_stage = "Seed" if max_ord == 0 else f"Series {chr(64+min(max_ord,26))}"
                method = "formal venture-round order fallback"
            else:
                max_ord = 0
                max_stage = "Seed"
                method = "pre-series fallback"
                missing_stage.append(name)
    if max_ord <= 0:
        stage4 = 1
    elif max_ord == 1:
        stage4 = 2
    elif max_ord == 2:
        stage4 = 3
    else:
        stage4 = 4
    out.append({
        "firm_id": int(float(key["firm_id"])), "OrganizationName": name,
        "VD": vd, "reference_year": ref_year, "stage4": stage4,
        "stage_label": {0:"Unclassified",1:"Seed",2:"Series A",3:"Series B",4:"Series C+"}[stage4],
        "max_series_at_reference": max_stage,
        "cutoff_date": cutoff.strftime("%Y-%m-%d"),
        "formal_rounds_by_reference": len(eligible),
        "stage_inference_method": method,
    })

with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=out[0].keys())
    w.writeheader(); w.writerows(out)

summary = {
    "dta_firms": len(keys), "panel_matched_names": len(panel), "crosswalk_rows": len(out),
    "unmatched_count": len(unmatched), "unmatched": unmatched,
    "pre_series_fallback_count": len(missing_stage), "pre_series_fallback": missing_stage,
    "stage_distribution": dict(Counter(r["stage_label"] for r in out)),
    "stage_by_vd": {f"VD={v}": dict(Counter(r["stage_label"] for r in out if r["VD"]==v)) for v in (0,1)},
    "inference_methods": dict(Counter(r["stage_inference_method"] for r in out)),
}
with open(SUMMARY, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print(json.dumps(summary, ensure_ascii=False, indent=2))
