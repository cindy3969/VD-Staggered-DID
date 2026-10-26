from pathlib import Path
import csv, io, re, zipfile
import pandas as pd

ROOT = Path(r"C:\Users\user\Documents\VD")
REF = ROOT / "outputs" / "claude_replication_reference" / "data"
OUT = ROOT / "outputs" / "csdid_union_corrected_3yr"
OUT.mkdir(parents=True, exist_ok=True)

apps = pd.read_csv(REF / "application_level_list_through2024_used.csv", low_memory=False)
panel = pd.read_csv(REF / "firm_year_panel_analysis.csv", low_memory=False)

# Confirmed firm-level false matches visible in the supplied review screenshot.
bad_firms = {152, 324, 2079, 5624, 5892}  # Click Notices, Geli, Anaconda, Veritas Genetics, BioSense
bad = apps["full_firm_id"].isin(bad_firms)

# Snap is only partly wrong: retain Snap Inc. and remove unrelated Snap-on/other entities.
snap_bad_pattern = r"snap[- ]on|snap cpap|snap mat|snap[- ]n[- ]go|snap-on equipment|snap-on tools"
snap_bad = apps["full_firm_id"].eq(1791) & apps["legacy_matched_assignee_labels"].fillna("").str.contains(
    snap_bad_pattern, case=False, regex=True
)
remove = bad | snap_bad
removed = apps.loc[remove].copy()
kept = apps.loc[~remove].copy()
removed.to_csv(OUT / "excluded_confirmed_bad_firm_patent_links.csv", index=False)

# Add titles to grant-only records using the grant patent table. A1 titles come
# from the independently rebuilt publication file.
a1 = pd.read_csv(
    ROOT / "outputs" / "patent_application_list_rebuilt_2024" /
    "patent_application_list_through_2024.csv", low_memory=False
)
def app_key(s):
    return s.astype(str).str.replace(r"\D", "", regex=True).str.lstrip("0")
kept["_appkey"] = app_key(kept["application_id"])
a1["_appkey"] = app_key(a1["application_id"])
title_map = (a1.dropna(subset=["patent_title"]).drop_duplicates(["full_firm_id", "_appkey"])
             .set_index(["full_firm_id", "_appkey"])["patent_title"])
kept["patent_title"] = [title_map.get((fid, key), "") for fid, key in zip(kept.full_firm_id, kept._appkey)]

needed = set()
for value in kept.loc[kept["patent_title"].eq(""), "grant_patent_ids"].dropna().astype(str):
    needed.update(re.findall(r"\d+", value))
title_by_patent = {}
zpath = ROOT / "outputs" / "patentsview_2024_full_cohort" / "source" / "g_patent.tsv.zip"
with zipfile.ZipFile(zpath) as zf:
    with zf.open(zf.namelist()[0]) as raw:
        reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace"), delimiter="\t")
        for row in reader:
            pid = str(row.get("patent_id", "")).strip()
            if pid in needed:
                title_by_patent[pid] = row.get("patent_title", "")
for idx in kept.index[kept["patent_title"].eq("")]:
    ids = re.findall(r"\d+", str(kept.at[idx, "grant_patent_ids"]))
    kept.at[idx, "patent_title"] = next((title_by_patent[x] for x in ids if title_by_patent.get(x)), "")

def norm_title(v):
    return " ".join(re.findall(r"[a-z0-9]+", str(v).casefold())) if pd.notna(v) else ""
kept["title_normalized"] = kept["patent_title"].map(norm_title)
kept["invention_key"] = kept["title_normalized"]
blank = kept["invention_key"].eq("")
kept.loc[blank, "invention_key"] = "application:" + kept.loc[blank, "_appkey"]

# Equal follow-up: filing cohorts through 2021 and grants within three years.
kept["filing_year"] = pd.to_numeric(kept["filing_year"], errors="coerce")
kept["grant_lag_years"] = pd.to_numeric(kept["grant_lag_years"], errors="coerce")
kept["granted_within_3y"] = (
    kept["ultimately_granted"].eq(1) & kept["grant_lag_years"].between(0, 3, inclusive="both")
).astype(int)
mature = kept.loc[kept["filing_year"].le(2021)].copy()

# Title sensitivity: one firm-title invention, assigned to its earliest filing year;
# grant=1 if any linked member application grants within three years.
inventions = (mature.sort_values(["full_firm_id", "invention_key", "filing_year", "application_id"])
    .groupby(["full_firm_id", "invention_key"], as_index=False)
    .agg(organization_name=("organization_name", "first"), patent_title=("patent_title", "first"),
         filing_year=("filing_year", "min"), granted_within_3y=("granted_within_3y", "max"),
         application_count_same_title=("application_id", "nunique"),
         member_application_ids=("application_id", lambda s: "|".join(sorted(set(s.astype(str)))))))

base = panel.loc[panel["year"].le(2021)].copy()
base["G"] = base["first_vd_year_G"].fillna(0).astype(int)
base["prior"] = base["prior_patent_G"]
base["early"] = base["early_stage_G_reconstructed"]
cnt = mature.groupby(["full_firm_id", "filing_year"], as_index=False)["granted_within_3y"].sum()
cnt = cnt.rename(columns={"filing_year": "year", "granted_within_3y": "granted_3yr_corrected"})
icnt = inventions.groupby(["full_firm_id", "filing_year"], as_index=False)["granted_within_3y"].sum()
icnt = icnt.rename(columns={"filing_year": "year", "granted_within_3y": "granted_3yr_title_dedup"})
base = base.merge(cnt, on=["full_firm_id", "year"], how="left").merge(icnt, on=["full_firm_id", "year"], how="left")
base[["granted_3yr_corrected", "granted_3yr_title_dedup"]] = base[["granted_3yr_corrected", "granted_3yr_title_dedup"]].fillna(0)

kept.drop(columns=["_appkey"]).to_csv(OUT / "application_level_union_corrected_visible_mismatches.csv", index=False)
inventions.to_csv(OUT / "title_deduplicated_inventions_through2021.csv", index=False)
base.to_csv(OUT / "hist_panel.csv", index=False)
base.to_stata(OUT / "firm_year_panel_corrected_3yr.dta", write_index=False, version=118)

qa = pd.DataFrame({"item": ["union_rows_original", "confirmed_bad_links_removed", "union_rows_retained",
    "mature_applications_through2021", "mature_title_deduplicated_inventions",
    "granted_within3y_applications", "granted_within3y_title_dedup"],
    "value": [len(apps), len(removed), len(kept), len(mature), len(inventions),
              mature.granted_within_3y.sum(), inventions.granted_within_3y.sum()]})
qa.to_csv(OUT / "cleaning_QA.csv", index=False)
print(qa.to_string(index=False))
