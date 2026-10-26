"""Add disclosure, claim, and grant-rate measures to the 2,820-firm Table 3 files."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import argparse
import html
import json
import re
import sys
import time
import zipfile

ROOT = Path(r"C:\Users\user\Documents\VD")
sys.path.insert(0, str(ROOT / ".artifact_work" / "textstat_deps"))
import numpy as np
import pandas as pd

import textstat  # noqa: E402

OUT = ROOT / "outputs" / "innovation_measures_2820"
APP_MEASURES = OUT / "granted_application_innovation_measures.csv"
ALL_APPS = ROOT / "outputs" / "csdid_union_corrected_3yr" / "application_level_union_corrected_visible_mismatches.csv"
TARGET = ROOT / "outputs" / "psm_final_2820_package" / "table3_current_2820_cross_section_v2"
CACHE = OUT / "patent_disclosure_claim_metrics_fast_cache.csv"
PV_SOURCE = ROOT / "outputs" / "patentsview_2024_full_cohort" / "source"
G_PATENT = PV_SOURCE / "g_patent.tsv.zip"
G_FIGURES = PV_SOURCE / "g_figures.tsv.zip"


def key(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


class PatentHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.description_depth = 0
        self.description_parts = []
        self.claim_depth = 0
        self.claim_parts = []
        self.claims = []
        self.itemprops = {}
        self.figure_pages = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        itemprop = attrs_dict.get("itemprop", "")
        if itemprop:
            self.itemprops.setdefault(itemprop, []).append(attrs_dict.get("content", ""))
        if itemprop == "figurePage" and attrs_dict.get("content") is not None:
            self.figure_pages.append(attrs_dict["content"])
        if self.description_depth:
            self.description_depth += 1
        elif itemprop == "description" and tag in {"section", "div"}:
            self.description_depth = 1
        classes = set(attrs_dict.get("class", "").split())
        if self.claim_depth:
            self.claim_depth += 1
        elif tag == "div" and "claim" in classes:
            self.claim_depth = 1
            self.claim_parts = []

    def handle_startendtag(self, tag, attrs):
        attrs_dict = dict(attrs)
        itemprop = attrs_dict.get("itemprop", "")
        if itemprop:
            self.itemprops.setdefault(itemprop, []).append(attrs_dict.get("content", ""))
        if itemprop == "figurePage" and attrs_dict.get("content") is not None:
            self.figure_pages.append(attrs_dict["content"])

    def handle_endtag(self, tag):
        if self.description_depth:
            self.description_depth -= 1
        if self.claim_depth:
            self.claim_depth -= 1
            if self.claim_depth == 0:
                text = re.sub(r"\s+", " ", " ".join(self.claim_parts)).strip()
                if text:
                    self.claims.append(text)
                self.claim_parts = []

    def handle_data(self, data):
        if self.description_depth:
            self.description_parts.append(data)
        if self.claim_depth:
            self.claim_parts.append(data)


def classify_claims(claims):
    cleaned = []
    for text in claims:
        text = re.sub(r"^\s*\d+\.?\s*", "", text).strip()
        if text and text not in cleaned:
            cleaned.append(text)
    dependent_pattern = re.compile(
        r"\b(?:claim|claims)\s+\d|\baccording\s+to\s+(?:any\s+of\s+)?(?:the\s+)?(?:preceding\s+)?claims?\b",
        re.I,
    )
    dependent = sum(bool(dependent_pattern.search(text[:500])) for text in cleaned)
    total = len(cleaned)
    return total, total - dependent, dependent


def readability_counts(text):
    """Single-pass English counts used by Fog, ARI, and Flesch formulas."""
    tokens = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text)
    words = max(len(tokens), 1)
    sentences = max(len(re.findall(r"[.!?]+(?:\s|$)", text)), 1)
    characters = sum(len(re.sub(r"[^A-Za-z0-9]", "", token)) for token in tokens)

    def syllables(token):
        word = re.sub(r"[^a-z]", "", token.lower())
        if len(word) <= 3:
            return 1
        count = len(re.findall(r"[aeiouy]+", word))
        if word.endswith("e") and not word.endswith(("le", "ye")) and count > 1:
            count -= 1
        if word.endswith("es") and not word.endswith(("aes", "ees", "oes")) and count > 1:
            count -= 1
        return max(count, 1)

    syllable_values = [syllables(token) for token in tokens]
    total_syllables = sum(syllable_values)
    difficult = sum(value >= 3 for value in syllable_values)
    return words, sentences, characters, total_syllables, difficult


def fetch_metrics(patent_id):
    url = f"https://patents.google.com/patent/US{patent_id}/en"
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; academic-research/1.0)"})
    for attempt in range(3):
        try:
            with urlopen(req, timeout=20) as response:
                body = response.read().decode("utf-8", errors="replace")
            parser = PatentHTMLParser()
            parser.feed(body)
            description = html.unescape(" ".join(parser.description_parts))
            description = re.sub(r"\s+", " ", description).strip()
            if not description:
                raise ValueError("description_not_found")
            total_claims, independent_claims, dependent_claims = classify_claims(parser.claims)
            words, sentences, characters, syllables, difficult = readability_counts(description)
            fog = 0.4 * ((words / sentences) + 100 * (difficult / words))
            ari = 4.71 * (characters / words) + 0.5 * (words / sentences) - 21.43
            flesch = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)

            # Google Patents exposes one figurePage value per image/figure.  The
            # number of distinct zero-based page values is the number of sheets.
            valid_pages = []
            for value in parser.figure_pages:
                try:
                    valid_pages.append(int(value))
                except (TypeError, ValueError):
                    pass
            number_sheets = len(set(valid_pages)) if valid_pages else 0
            # A single figure can be tiled into repeated figurePage metadata.
            # Count explicit figure labels in the description, deduplicated.
            figure_labels = re.findall(r"\bFIG(?:URE)?\.?\s*([0-9]+[A-Z]?)\b", description, re.I)
            number_figures = len({x.upper() for x in figure_labels})

            return {
                "patent_id": int(patent_id),
                "gunning_fog": float(fog),
                "automated_readability_index": float(ari),
                "flesch_reading_ease": flesch,
                "neg_flesch_reading": -flesch,
                "number_figures": int(number_figures),
                "number_sheets": int(number_sheets),
                "number_claims": int(total_claims),
                "independent_claims": int(independent_claims),
                "dependent_claims": int(dependent_claims),
                "metric_status": "ok",
            }
        except HTTPError as exc:
            if exc.code in (404, 410):
                return {"patent_id": int(patent_id), "metric_status": f"http_{exc.code}"}
        except (URLError, TimeoutError, ValueError):
            pass
        time.sleep(1.5 * (attempt + 1))
    return {"patent_id": int(patent_id), "metric_status": "request_failed"}


def collect_metrics(patent_ids):
    cols = ["patent_id", "gunning_fog", "automated_readability_index", "flesch_reading_ease",
            "neg_flesch_reading", "number_figures", "number_sheets", "number_claims",
            "independent_claims", "dependent_claims", "metric_status"]
    cached = pd.read_csv(CACHE) if CACHE.exists() else pd.DataFrame(columns=cols)
    for col in cols:
        if col not in cached:
            cached[col] = np.nan
    cached = cached[cols]
    done = set(pd.to_numeric(cached.patent_id, errors="coerce").dropna().astype(int))
    todo = sorted(set(int(x) for x in patent_ids) - done)
    rows = []
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = {pool.submit(fetch_metrics, pid): pid for pid in todo}
        for i, future in enumerate(as_completed(futures), 1):
            rows.append(future.result())
            if i % 100 == 0:
                cached = pd.concat([cached, pd.DataFrame(rows)], ignore_index=True)
                cached = cached[cols].drop_duplicates("patent_id", keep="last")
                cached.to_csv(CACHE, index=False, encoding="utf-8-sig")
                rows = []
                print(f"patent text progress: {i:,}/{len(todo):,}", flush=True)
    if rows:
        cached = pd.concat([cached, pd.DataFrame(rows)], ignore_index=True)
    cached = cached[cols].drop_duplicates("patent_id", keep="last").sort_values("patent_id")
    cached.to_csv(CACHE, index=False, encoding="utf-8-sig")
    return cached


def read_patentsview_subset(path, patent_ids, columns):
    """Read only target patents from an official zipped PatentsView TSV."""
    wanted = set(str(int(x)) for x in patent_ids)
    chunks = []
    with zipfile.ZipFile(path) as archive:
        member = archive.namelist()[0]
        with archive.open(member) as stream:
            for chunk in pd.read_csv(stream, sep="\t", usecols=columns, dtype={"patent_id": str},
                                     chunksize=500_000, low_memory=False):
                hit = chunk.loc[chunk.patent_id.isin(wanted)]
                if not hit.empty:
                    chunks.append(hit)
    return pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame(columns=columns)


def inspect_html(patent_id):
    req = Request(f"https://patents.google.com/patent/US{patent_id}/en", headers={"User-Agent": "Mozilla/5.0"})
    body = urlopen(req, timeout=30).read().decode("utf-8", errors="replace")
    parser = PatentHTMLParser(); parser.feed(body)
    print(json.dumps({
        "patent_id": patent_id,
        "itemprops": {k: v[:10] for k, v in parser.itemprops.items() if re.search("claim|fig|sheet|draw", k, re.I)},
        "figure_page_values": parser.figure_pages[:30],
        "figure_page_count": len(parser.figure_pages),
        "figure_page_unique": sorted(set(parser.figure_pages)),
        "claim_div_count": len(parser.claims),
        "claim_samples": parser.claims[:3],
        "raw_count_matches": {pattern: re.findall(pattern + r".{0,120}", body, re.I)[:5]
                              for pattern in ["num.?fig", "num.?sheet", "number.of.draw", "number.of.fig"]},
    }, ensure_ascii=False, indent=2))


def main():
    app = pd.read_csv(APP_MEASURES, low_memory=False)
    # Only t+1..t+3 enters the requested cross-sectional outcome window.
    patent_ids = pd.to_numeric(
        app.loc[app.event_time.between(1, 3), "primary_grant_patent_id"], errors="coerce").dropna().astype(int)
    metrics = collect_metrics(patent_ids)
    ok = metrics.loc[metrics.metric_status.eq("ok")].drop(columns="metric_status")
    official_claims = read_patentsview_subset(G_PATENT, patent_ids, ["patent_id", "num_claims"])
    official_figures = read_patentsview_subset(
        G_FIGURES, patent_ids, ["patent_id", "num_figures", "num_sheets"])
    official = official_claims.merge(official_figures, on="patent_id", how="outer", validate="one_to_one")
    official["patent_id"] = pd.to_numeric(official.patent_id, errors="coerce").astype("Int64")
    ok = ok.merge(official, on="patent_id", how="left", validate="one_to_one")
    ok["html_number_claims"] = ok["number_claims"]
    ok["number_claims"] = pd.to_numeric(ok["num_claims"], errors="coerce").combine_first(ok["number_claims"])
    ok["number_figures"] = pd.to_numeric(ok["num_figures"], errors="coerce").combine_first(ok["number_figures"])
    ok["number_sheets"] = pd.to_numeric(ok["num_sheets"], errors="coerce").combine_first(ok["number_sheets"])
    # Preserve the independently parsed independent-claim count, and reconcile
    # dependent claims to the official total claim count.
    valid = ok.number_claims.notna() & ok.independent_claims.notna() & (ok.number_claims >= ok.independent_claims)
    ok.loc[valid, "dependent_claims"] = ok.loc[valid, "number_claims"] - ok.loc[valid, "independent_claims"]
    ok = ok.drop(columns=["num_claims", "num_figures", "num_sheets"])
    app = app.drop(columns=[c for c in ok.columns if c != "patent_id" and c in app], errors="ignore")
    app = app.merge(ok, left_on="primary_grant_patent_id", right_on="patent_id", how="left", validate="many_to_one")
    app = app.drop(columns="patent_id")
    app.to_csv(APP_MEASURES, index=False, encoding="utf-8-sig")

    window = app.loc[app.event_time.between(1, 3)].copy()
    metric_cols = ["gunning_fog", "automated_readability_index", "neg_flesch_reading",
                   "number_figures", "number_sheets", "number_claims",
                   "independent_claims", "dependent_claims"]
    agg = window.groupby(window.organization_name.map(key))[metric_cols].mean().reset_index()
    agg = agg.rename(columns={"organization_name": "name_key", **{
        "gunning_fog": "gunning_fog_mean_win3",
        "automated_readability_index": "ari_mean_win3",
        "neg_flesch_reading": "neg_flesch_mean_win3",
        "number_figures": "figures_mean_win3",
        "number_sheets": "sheets_mean_win3",
        "number_claims": "claims_mean_win3",
        "independent_claims": "indep_claims_mean_win3",
        "dependent_claims": "dep_claims_mean_win3",
    }})

    all_apps = pd.read_csv(ALL_APPS, low_memory=False)
    target = pd.read_csv(TARGET.with_suffix(".csv"), low_memory=False)
    ref = target[["OrganizationName", "VDyear"]].copy()
    ref["name_key"] = ref.OrganizationName.map(key)
    all_apps["name_key"] = all_apps.organization_name.map(key)
    all_apps = all_apps.merge(ref[["name_key", "VDyear"]], on="name_key", how="inner", validate="many_to_one")
    all_apps["event_time_vd"] = all_apps.filing_year - all_apps.VDyear
    grant_source = all_apps.loc[all_apps.event_time_vd.between(1, 3)].drop_duplicates(
        ["name_key", "application_id"])
    grant = grant_source.groupby("name_key", as_index=False).agg(
        applications_filed_win3=("application_id", "nunique"),
        applications_granted_win3=("ultimately_granted", "sum"))
    grant["grant_rate_win3"] = grant.applications_granted_win3 / grant.applications_filed_win3

    new_cols = [c for c in agg.columns if c != "name_key"] + ["applications_filed_win3",
                "applications_granted_win3", "grant_rate_win3"]
    target = target.drop(columns=[c for c in new_cols if c in target], errors="ignore")
    target["name_key"] = target.OrganizationName.map(key)
    target = target.merge(agg, on="name_key", how="left", validate="one_to_one")
    target = target.merge(grant, on="name_key", how="left", validate="one_to_one").drop(columns="name_key")
    for col in ["applications_filed_win3", "applications_granted_win3"]:
        target[col] = target[col].fillna(0).astype(int)
    target.to_csv(TARGET.with_suffix(".csv"), index=False, encoding="utf-8-sig")

    old_raw = pd.read_stata(TARGET.with_suffix(".dta"), convert_categoricals=False)
    old_labeled = pd.read_stata(TARGET.with_suffix(".dta"))
    value_labels = {}
    for variable in ["Region2", "Industry2"]:
        pairs = pd.DataFrame({"code": old_raw[variable].astype(int),
                              "label": old_labeled[variable].astype(str)}).drop_duplicates()
        value_labels[variable] = dict(zip(pairs.code, pairs.label))
    dta = target.drop(columns=[c for c in ["Region2_label", "Industry2_label"] if c in target])
    for col in dta.select_dtypes(include=["object", "string"]).columns:
        dta[col] = dta[col].fillna("").astype(str)
    labels = {
        "gunning_fog_mean_win3": "Mean Gunning Fog, granted applications filed t+1 to t+3",
        "ari_mean_win3": "Mean ARI, granted applications filed t+1 to t+3",
        "neg_flesch_mean_win3": "Mean negative Flesch reading, granted applications filed t+1 to t+3",
        "figures_mean_win3": "Mean figures, granted applications filed t+1 to t+3",
        "sheets_mean_win3": "Mean sheets, granted applications filed t+1 to t+3",
        "claims_mean_win3": "Mean claims, granted applications filed t+1 to t+3",
        "indep_claims_mean_win3": "Mean independent claims, granted applications filed t+1 to t+3",
        "dep_claims_mean_win3": "Mean dependent claims, granted applications filed t+1 to t+3",
        "applications_filed_win3": "Applications filed t+1 to t+3",
        "applications_granted_win3": "Eventually granted applications filed t+1 to t+3",
        "grant_rate_win3": "Eventually granted / filed applications, t+1 to t+3",
    }
    dta.to_stata(TARGET.with_suffix(".dta"), write_index=False, version=118,
                 value_labels=value_labels, variable_labels=labels)

    qa = {
        "patent_rows": int(len(app)),
        "patent_metric_coverage": {c: int(app[c].notna().sum()) for c in metric_cols},
        "metric_status": metrics.metric_status.value_counts(dropna=False).to_dict(),
        "cross_section_rows": int(len(target)),
        "firms_with_granted_patent_metrics_win3": int(target["gunning_fog_mean_win3"].notna().sum()),
        "firms_with_filed_applications_win3": int(target.grant_rate_win3.notna().sum()),
        "formulas": {
            "text_counts": "single-pass English word/sentence/character counts; syllables from vowel-group heuristic",
            "gunning_fog": "0.4*((words/sentences)+100*(words with >=3 syllables/words))",
            "automated_readability_index": "4.71*(characters/words)+0.5*(words/sentences)-21.43",
            "flesch_reading_ease": "206.835-1.015*(words/sentences)-84.6*(syllables/words); multiplied by -1",
            "grant_rate": "eventually granted applications / all applications filed in t+1..t+3",
        },
    }
    (OUT / "disclosure_claim_grant_QA.json").write_text(json.dumps(qa, indent=2), encoding="utf-8")
    print(json.dumps(qa, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inspect", type=int)
    args = parser.parse_args()
    if args.inspect:
        inspect_html(args.inspect)
    else:
        main()
