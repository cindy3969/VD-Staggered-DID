"""Build no-citation, breakthrough, and patent-description-length measures.

Definitions follow Appendix A of Innovation Management (2025). Citation data
are observed through the local 2024 PatentsView snapshot. Breakthrough cutoffs
are computed from the full granted-patent universe by filing year and primary
three-digit CPC class. Description word counts are collected only for patents
belonging to the matched 2,820 firms in event years -4..+4.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import html
from html.parser import HTMLParser
import json
import math
import re
import time
import zipfile
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd


class DescriptionParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if self.depth:
            self.depth += 1
        elif attr.get("itemprop") == "description":
            self.depth = 1

    def handle_startendtag(self, tag, attrs):
        return

    def handle_endtag(self, tag):
        if self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth:
            self.parts.append(data)


ROOT = Path(r"C:\Users\user\Documents\VD")
OUT = ROOT / "outputs" / "innovation_measures_2820"
OUT.mkdir(parents=True, exist_ok=True)
PV = ROOT / "outputs" / "patentsview_2024_full_cohort" / "source"
APP_FILE = ROOT / "outputs" / "csdid_union_corrected_3yr" / "application_level_union_corrected_visible_mismatches.csv"
METHOD_FILE = ROOT / "outputs" / "table2_forward_citation_year_methods_39249" / "application_level_with_forward_citation_methods.csv"
GRID_FILE = ROOT / "outputs" / "table2_forward_citation_year_methods_39249" / "application_citation_year_grid.csv"
MATCHED_FILE = ROOT / "outputs" / "psm_final_2820_package" / "psm_stata_matched_2820.dta"
BASE_PANEL = ROOT / "outputs" / "table2_forward_citation_year_methods_39249" / "firm_year_with_citations.csv"
TARGET_STEM = ROOT / "outputs" / "psm_final_2820_package" / "table3_current_2820_cross_section_v2"
CACHE = OUT / "description_word_count_cache.csv"


def key(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def zip_stream(path: Path):
    archive = zipfile.ZipFile(path)
    member = next(n for n in archive.namelist() if not n.endswith("/"))
    return archive, archive.open(member)


def clean_ids(value):
    if pd.isna(value):
        return []
    return list(dict.fromkeys(int(x) for x in re.findall(r"\d+", str(value))))


def primary_cpc_for_patents(target_ids: set[int] | None = None):
    path = PV / "g_cpc_current.tsv.zip"
    z, s = zip_stream(path)
    try:
        header = pd.read_csv(s, sep="\t", nrows=0).columns.tolist()
    finally:
        s.close(); z.close()
    group_col = next(c for c in ["cpc_group_id", "cpc_subgroup_id", "cpc_class", "cpc_class_id"] if c in header)
    seq_col = next((c for c in ["cpc_sequence", "sequence"] if c in header), None)
    cols = ["patent_id", group_col] + ([seq_col] if seq_col else [])
    pieces = []
    z, s = zip_stream(path)
    try:
        for chunk in pd.read_csv(s, sep="\t", usecols=cols, dtype="string", chunksize=1_500_000):
            chunk["patent_id"] = pd.to_numeric(chunk["patent_id"], errors="coerce").astype("Int64")
            if target_ids is not None:
                chunk = chunk.loc[chunk["patent_id"].isin(target_ids)]
            if len(chunk):
                pieces.append(chunk)
    finally:
        s.close(); z.close()
    cpc = pd.concat(pieces, ignore_index=True)
    if seq_col:
        cpc["_seq"] = pd.to_numeric(cpc[seq_col], errors="coerce").fillna(999999)
        cpc = cpc.sort_values(["patent_id", "_seq"])
    cpc["cpc3"] = cpc[group_col].fillna("").str.upper().str.extract(r"([A-HY]\d{2})", expand=False)
    return cpc.dropna(subset=["patent_id", "cpc3"]).drop_duplicates("patent_id")[["patent_id", "cpc3"]]


def build_universe_thresholds():
    cache = OUT / "breakthrough_thresholds_full_universe.csv"
    member_cache = OUT / "breakthrough_members_full_universe.csv"
    if cache.exists() and member_cache.exists():
        return pd.read_csv(cache), pd.read_csv(member_cache)

    # Filing cohorts for the full granted-patent universe.
    z, s = zip_stream(PV / "g_application.tsv.zip")
    try:
        header = pd.read_csv(s, sep="\t", nrows=0).columns.tolist()
        date_col = next(c for c in ["filing_date", "application_date"] if c in header)
    finally:
        s.close(); z.close()
    z, s = zip_stream(PV / "g_application.tsv.zip")
    try:
        apps = pd.read_csv(s, sep="\t", usecols=["patent_id", date_col], dtype="string")
    finally:
        s.close(); z.close()
    apps["patent_id"] = pd.to_numeric(apps.patent_id, errors="coerce").astype("Int64")
    apps["filing_year"] = pd.to_datetime(apps[date_col], errors="coerce").dt.year.astype("Int64")
    apps = apps.loc[apps.filing_year.between(2010, 2024)].dropna(subset=["patent_id"]).drop_duplicates("patent_id")
    eligible = set(apps.patent_id.astype(int))

    # Count distinct citing patents for every eligible cited patent.
    z, s = zip_stream(PV / "g_us_patent_citation.tsv.zip")
    try:
        header = pd.read_csv(s, sep="\t", nrows=0).columns.tolist()
    finally:
        s.close(); z.close()
    cited_col = next(c for c in ["citation_patent_id", "cited_patent_id"] if c in header)
    citing_col = next(c for c in ["patent_id", "citing_patent_id"] if c in header)
    counts = {}
    z, s = zip_stream(PV / "g_us_patent_citation.tsv.zip")
    try:
        for chunk in pd.read_csv(s, sep="\t", usecols=[cited_col, citing_col], dtype="string", chunksize=2_000_000):
            chunk[cited_col] = pd.to_numeric(chunk[cited_col], errors="coerce").astype("Int64")
            x = chunk.loc[chunk[cited_col].isin(eligible), [cited_col, citing_col]].drop_duplicates()
            for pid, n in x.groupby(cited_col)[citing_col].nunique().items():
                counts[int(pid)] = counts.get(int(pid), 0) + int(n)
    finally:
        s.close(); z.close()
    apps["forward_citations_through_2024"] = apps.patent_id.map(counts).fillna(0).astype(int)
    cpc = primary_cpc_for_patents(eligible)
    universe = apps.merge(cpc, on="patent_id", how="inner", validate="one_to_one")
    # Select exactly ceil(5%) within each cell.  Citation ties at the boundary
    # are broken deterministically by ascending patent_id.
    universe = universe.sort_values(
        ["filing_year", "cpc3", "forward_citations_through_2024", "patent_id"],
        ascending=[True, True, False, True])
    universe["citation_rank"] = universe.groupby(["filing_year", "cpc3"]).cumcount() + 1
    universe["universe_patents"] = universe.groupby(["filing_year", "cpc3"])["patent_id"].transform("size")
    universe["top5_slots"] = np.ceil(universe.universe_patents * .05).astype(int)
    members = universe.loc[universe.citation_rank.le(universe.top5_slots),
                           ["patent_id", "filing_year", "cpc3", "forward_citations_through_2024"]].copy()
    members.to_csv(member_cache, index=False, encoding="utf-8-sig")
    thresholds = (members.groupby(["filing_year", "cpc3"])["forward_citations_through_2024"]
                  .min().rename("p95_forward_citations").reset_index())
    sizes = universe.groupby(["filing_year", "cpc3"]).size().rename("universe_patents").reset_index()
    thresholds = thresholds.merge(sizes, on=["filing_year", "cpc3"], validate="one_to_one")
    thresholds.to_csv(cache, index=False, encoding="utf-8-sig")
    return thresholds, members


def description_word_count(patent_id: int):
    url = f"https://patents.google.com/patent/US{patent_id}/en"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; academic-research/1.0)"}
    for attempt in range(2):
        try:
            request = Request(url, headers=headers)
            with urlopen(request, timeout=12) as response:
                status = response.status
                body = response.read().decode("utf-8", errors="replace")
            if status == 200:
                parser = DescriptionParser()
                parser.feed(body)
                if not parser.parts:
                    return patent_id, np.nan, "description_not_found"
                text = html.unescape(" ".join(parser.parts))
                words = re.findall(r"\b[\w]+(?:[-'][\w]+)*\b", text, flags=re.UNICODE)
                return patent_id, len(words), "ok"
            if status in (404, 410):
                return patent_id, np.nan, f"http_{status}"
        except HTTPError as exc:
            if exc.code in (404, 410):
                return patent_id, np.nan, f"http_{exc.code}"
        except (URLError, TimeoutError):
            pass
        time.sleep(1.5 * (attempt + 1))
    return patent_id, np.nan, "request_failed"


def collect_descriptions(target_ids):
    if CACHE.exists():
        cached = pd.read_csv(CACHE)
    else:
        cached = pd.DataFrame(columns=["patent_id", "description_word_count", "description_status"])
    cached["patent_id"] = pd.to_numeric(cached.patent_id, errors="coerce").astype("Int64")
    done = set(cached["patent_id"].dropna().astype(int))
    todo = sorted(set(target_ids) - done)
    rows = []
    with ThreadPoolExecutor(max_workers=32) as pool:
        futures = {pool.submit(description_word_count, pid): pid for pid in todo}
        for i, future in enumerate(as_completed(futures), 1):
            rows.append(future.result())
            if i % 250 == 0:
                update = pd.DataFrame(rows, columns=cached.columns)
                cached = pd.concat([cached, update], ignore_index=True).drop_duplicates("patent_id", keep="last")
                cached.to_csv(CACHE, index=False, encoding="utf-8-sig")
                rows = []
                print(f"description progress: {i:,}/{len(todo):,}", flush=True)
    if rows:
        cached = pd.concat([cached, pd.DataFrame(rows, columns=cached.columns)], ignore_index=True)
    cached = cached.drop_duplicates("patent_id", keep="last").sort_values("patent_id")
    cached.to_csv(CACHE, index=False, encoding="utf-8-sig")
    return cached


def main():
    matched = pd.read_stata(MATCHED_FILE, convert_categoricals=False)
    matched["name_key"] = matched.OrganizationName.map(key)
    ref = matched[["name_key", "VDYear"]].drop_duplicates()
    assert ref.name_key.is_unique

    apps = pd.read_csv(APP_FILE, dtype={"application_id": "string"}, low_memory=False)
    apps = apps.drop_duplicates(["full_firm_id", "application_id"]).copy()
    apps["name_key"] = apps.organization_name.map(key)
    apps = apps.merge(ref.rename(columns={"VDYear": "reference_year"}), on="name_key", how="inner", validate="many_to_one")
    apps["event_time"] = apps.filing_year - apps.reference_year
    apps = apps.loc[apps.event_time.between(-4, 4) & apps.ultimately_granted.eq(1)].copy()

    methods = pd.read_csv(METHOD_FILE, usecols=["application_id", "fwd_raw_total"], dtype={"application_id": "string"})
    grid = pd.read_csv(GRID_FILE, usecols=["application_id", "cpc3"], dtype={"application_id": "string"}).drop_duplicates("application_id")
    apps = apps.merge(methods, on="application_id", how="left", validate="one_to_one")
    apps = apps.merge(grid, on="application_id", how="left", validate="one_to_one")
    apps["fwd_raw_total"] = apps.fwd_raw_total.fillna(0).astype(int)
    apps["no_citation"] = apps.fwd_raw_total.eq(0).astype(int)

    thresholds, breakthrough_members = build_universe_thresholds()
    apps = apps.merge(thresholds, on=["filing_year", "cpc3"], how="left", validate="many_to_one")
    apps["primary_grant_patent_id"] = apps.grant_patent_ids.map(
        lambda value: clean_ids(value)[0] if clean_ids(value) else np.nan)
    breakthrough_ids = set(breakthrough_members.patent_id.astype(int))
    apps["breakthrough_patent"] = np.where(
        apps.p95_forward_citations.notna(),
        apps.primary_grant_patent_id.isin(breakthrough_ids).astype(int), np.nan)

    exploded = []
    for row in apps[["application_id", "grant_patent_ids"]].itertuples(index=False):
        for pid in clean_ids(row.grant_patent_ids):
            exploded.append((str(row.application_id), pid))
    grants = pd.DataFrame(exploded, columns=["application_id", "patent_id"]).drop_duplicates()
    desc = collect_descriptions(set(grants.patent_id))
    grants = grants.merge(desc, on="patent_id", how="left", validate="many_to_one")
    desc_app = grants.groupby("application_id", as_index=False).agg(
        description_word_count=("description_word_count", "sum"),
        description_patents_found=("description_word_count", "count"),
        description_grant_documents=("patent_id", "nunique"))
    desc_app.loc[desc_app.description_patents_found.eq(0), "description_word_count"] = np.nan
    apps = apps.merge(desc_app, on="application_id", how="left", validate="one_to_one")
    apps["ln_description_words"] = np.log(apps.description_word_count.where(apps.description_word_count.gt(0)))

    app_cols = ["full_firm_id", "organization_name", "application_id", "filing_date", "filing_year",
                "reference_year", "event_time", "grant_patent_ids", "primary_grant_patent_id", "cpc3", "fwd_raw_total",
                "no_citation", "p95_forward_citations", "universe_patents", "breakthrough_patent",
                "description_word_count", "ln_description_words", "description_patents_found",
                "description_grant_documents"]
    apps[app_cols].to_csv(OUT / "granted_application_innovation_measures.csv", index=False, encoding="utf-8-sig")

    fy = apps.groupby(["name_key", "filing_year"], as_index=False).agg(
        granted_applications_measured=("application_id", "nunique"),
        no_citation_count=("no_citation", "sum"),
        no_citation_share=("no_citation", "mean"),
        breakthrough_patent_count=("breakthrough_patent", "sum"),
        breakthrough_patent_share=("breakthrough_patent", "mean"),
        description_words_mean=("description_word_count", "mean"),
        ln_description_words_mean=("ln_description_words", "mean"),
        description_apps_measured=("description_word_count", "count"))
    panel = pd.read_csv(BASE_PANEL, low_memory=False)
    panel["name_key"] = panel.organization_name.map(key)
    panel = panel.sort_values(["name_key", "year", "full_firm_id"]).drop_duplicates(["name_key", "year"])
    grid_rows = []
    for row in matched[["no", "OrganizationName", "name_key", "VDYear"]].itertuples(index=False):
        for event in range(-4, 5):
            grid_rows.append((int(row.no), row.OrganizationName, row.name_key,
                              int(row.VDYear), event, int(row.VDYear) + event))
    panel_grid = pd.DataFrame(grid_rows, columns=["firm_id_2820", "OrganizationName", "name_key",
                                                  "reference_year", "event_time_vd", "year"])
    panel = panel_grid.merge(panel, on=["name_key", "year"], how="left", validate="one_to_one")
    assert not fy[["name_key", "filing_year"]].duplicated().any()
    panel = panel.merge(fy, left_on=["name_key", "year"], right_on=["name_key", "filing_year"],
                        how="left", validate="many_to_one").drop(columns=["filing_year", "name_key"])
    count_cols = ["granted_applications_measured", "no_citation_count", "breakthrough_patent_count", "description_apps_measured"]
    panel[count_cols] = panel[count_cols].fillna(0).astype(int)
    panel.to_csv(OUT / "firm_year_tminus4_tplus4_with_innovation_measures.csv", index=False, encoding="utf-8-sig")
    dta_panel = panel.copy()
    for col in dta_panel.select_dtypes(include=["object", "string"]).columns:
        dta_panel[col] = dta_panel[col].fillna("").astype(str)
    dta_panel.to_stata(OUT / "firm_year_tminus4_tplus4_with_innovation_measures.dta", write_index=False, version=118)

    win = apps.loc[apps.event_time.between(1, 3)].groupby("name_key", as_index=False).agg(
        no_citation_share_win3=("no_citation", "mean"),
        breakthrough_patent_share_win3=("breakthrough_patent", "mean"),
        description_words_mean_win3=("description_word_count", "mean"),
        ln_description_words_mean_win3=("ln_description_words", "mean"),
        innovation_granted_apps_win3=("application_id", "nunique"),
        description_apps_measured_win3=("description_word_count", "count"))
    target = pd.read_csv(TARGET_STEM.with_suffix(".csv"), low_memory=False)
    target["name_key"] = target.OrganizationName.map(key)
    new_cols = ["no_citation_share_win3", "breakthrough_patent_share_win3",
                "description_words_mean_win3", "ln_description_words_mean_win3",
                "innovation_granted_apps_win3", "description_apps_measured_win3"]
    target = target.drop(columns=[c for c in new_cols if c in target], errors="ignore")
    target = target.merge(win, on="name_key", how="left", validate="one_to_one").drop(columns="name_key")
    target["innovation_granted_apps_win3"] = target.innovation_granted_apps_win3.fillna(0).astype(int)
    target["description_apps_measured_win3"] = target.description_apps_measured_win3.fillna(0).astype(int)
    target.to_csv(TARGET_STEM.with_suffix(".csv"), index=False, encoding="utf-8-sig")

    old = pd.read_stata(TARGET_STEM.with_suffix(".dta"), convert_categoricals=False)
    value_labels = {}
    labeled = pd.read_stata(TARGET_STEM.with_suffix(".dta"))
    for variable in ["Region2", "Industry2"]:
        pairs = pd.DataFrame({"code": old[variable].astype(int), "label": labeled[variable].astype(str)}).drop_duplicates()
        value_labels[variable] = dict(zip(pairs.code, pairs.label))
    dta_target = target.drop(columns=[c for c in ["Region2_label", "Industry2_label"] if c in target])
    for col in dta_target.select_dtypes(include=["object", "string"]).columns:
        dta_target[col] = dta_target[col].fillna("").astype(str)
    var_labels = {
        "no_citation_share_win3": "Share of granted applications filed t+1 to t+3 with zero future citations",
        "breakthrough_patent_share_win3": "Share of granted applications filed t+1 to t+3 at/above CPC3-year citation p95",
        "description_words_mean_win3": "Mean description word count for granted applications filed t+1 to t+3",
        "ln_description_words_mean_win3": "Mean ln(description words) for granted applications filed t+1 to t+3",
        "innovation_granted_apps_win3": "Granted applications used for innovation measures in t+1 to t+3",
        "description_apps_measured_win3": "Granted applications with description text in t+1 to t+3",
    }
    dta_target.to_stata(TARGET_STEM.with_suffix(".dta"), write_index=False, version=118,
                        value_labels=value_labels, variable_labels=var_labels)

    qa = {
        "citation_cutoff_year": 2024,
        "breakthrough_benchmark": "full PatentsView granted-patent universe, filing year x primary CPC3",
        "breakthrough_rule": "exact ceil(5%) per filing-year x CPC3 cell; citations descending; boundary ties by ascending patent_id",
        "application_rows_event_minus4_plus4": int(len(apps)),
        "application_rows_win3": int(apps.event_time.between(1, 3).sum()),
        "description_applications_measured": int(apps.description_word_count.notna().sum()),
        "description_coverage": float(apps.description_word_count.notna().mean()),
        "cross_section_rows": int(len(target)),
        "cross_section_treated": int(target.VD.sum()),
        "missing_cpc_breakthrough": int(apps.breakthrough_patent.isna().sum()),
    }
    (OUT / "QA_summary.json").write_text(json.dumps(qa, indent=2), encoding="utf-8")
    print(json.dumps(qa, indent=2), flush=True)


if __name__ == "__main__":
    main()
