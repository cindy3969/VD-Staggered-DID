"""Rebuild full-cohort ultimately-granted application counts at the PSM reference year.

The script streams the official PatentsView 2024 ZIP archives and never extracts
them. It intentionally reads only VD-project inputs.
"""
from __future__ import annotations

import csv
import io
import re
import zipfile
from collections import defaultdict
from pathlib import Path

import pandas as pd


ROOT = Path(r"C:\Users\user\Documents\VD")
PKG = ROOT / "outputs" / "psm_final_2820_package"
REC = ROOT / "outputs" / "patent_panel_recovery"
SRC = ROOT / "outputs" / "patentsview_2024_full_cohort" / "source"
BASE = PKG / "v4_rebuilt_matching_covariates_7316_without_patents.dta"
TREATMENT = ROOT / "outputs" / "full_cohort_treatment_audit" / "full_cohort_treatment_definition_7316.dta"

SUFFIXES = {
    "inc", "incorporated", "corp", "corporation", "co", "company", "llc",
    "ltd", "limited", "lp", "llp", "plc", "holdings", "holding",
}


def norm(value: object) -> str:
    words = re.findall(r"[a-z0-9]+", str(value or "").casefold().replace("&", " and "))
    while words and words[-1] in SUFFIXES:
        words.pop()
    return " ".join(words)


def zip_rows(path: Path):
    if not zipfile.is_zipfile(path):
        raise FileNotFoundError(f"Valid PatentsView archive not found: {path}")
    with zipfile.ZipFile(path) as zf:
        with zf.open(zf.namelist()[0]) as raw:
            with io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace", newline="") as text:
                yield from csv.DictReader(text, delimiter="\t")


def main() -> None:
    REC.mkdir(parents=True, exist_ok=True)
    firms = pd.read_stata(BASE, convert_categoricals=False)
    if "full_firm_id" not in firms.columns:
        treatment = pd.read_stata(TREATMENT, convert_categoricals=False)
        treatment = treatment[["full_firm_id", "organization_name"]].drop_duplicates("full_firm_id")
        treatment["name_key"] = treatment.organization_name.map(norm)
        firms["name_key"] = firms.organization_name.map(norm)
        firms = treatment[["full_firm_id", "name_key"]].merge(
            firms, on="name_key", how="left", validate="one_to_one"
        )
    firms = firms.drop_duplicates("full_firm_id").copy()
    firms["reference_year"] = pd.to_numeric(firms["reference_year"], errors="coerce")

    name_to_firms: dict[str, list[int]] = defaultdict(list)
    firm_name: dict[int, str] = {}
    for row in firms.itertuples(index=False):
        fid = int(row.full_firm_id)
        firm_name[fid] = str(row.organization_name)
        key = norm(row.organization_name)
        if key:
            name_to_firms[key].append(fid)

    # Optional manually verified alias file. Expected columns:
    # full_firm_id, alias_name, accepted (1/0).
    alias_file = REC / "verified_firm_aliases.csv"
    if alias_file.exists():
        aliases = pd.read_csv(alias_file)
        aliases = aliases[pd.to_numeric(aliases.get("accepted", 1), errors="coerce").fillna(0).eq(1)]
        for row in aliases.itertuples(index=False):
            key = norm(row.alias_name)
            if key:
                name_to_firms[key].append(int(row.full_firm_id))

    patent_firms: dict[str, set[int]] = defaultdict(set)
    for filename, field in [
        ("g_assignee_disambiguated.tsv.zip", "disambig_assignee_organization"),
        ("g_assignee_not_disambiguated.tsv.zip", "raw_assignee_organization"),
    ]:
        for row in zip_rows(SRC / filename):
            key = norm(row.get(field, ""))
            fids = name_to_firms.get(key, ())
            if not fids:
                continue
            pid = str(row.get("patent_id", "")).strip()
            if pid:
                patent_firms[pid].update(fids)

    valid_patents: set[str] = set()
    for row in zip_rows(SRC / "g_patent.tsv.zip"):
        pid = str(row.get("patent_id", "")).strip()
        if pid not in patent_firms:
            continue
        if str(row.get("patent_type", "")).casefold() == "utility" and str(row.get("withdrawn", "")) in {"", "0"}:
            valid_patents.add(pid)

    app_rows: list[dict[str, object]] = []
    for row in zip_rows(SRC / "g_application.tsv.zip"):
        pid = str(row.get("patent_id", "")).strip()
        if pid not in valid_patents:
            continue
        date = str(row.get("filing_date", ""))
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            continue
        year = int(date[:4])
        application_id = re.sub(r"\D", "", str(row.get("application_id", ""))) or f"PATENT_{pid}"
        owners = sorted(patent_firms[pid])
        # Exact-name collisions are retained in an audit and excluded from the
        # analysis count until ownership is resolved.
        if len(owners) != 1:
            for fid in owners:
                app_rows.append({
                    "full_firm_id": fid, "organization_name": firm_name[fid],
                    "application_id": application_id, "patent_id": pid,
                    "filing_date": date, "filing_year": year,
                    "ownership_status": "multi_firm_name_collision",
                })
            continue
        fid = owners[0]
        app_rows.append({
            "full_firm_id": fid, "organization_name": firm_name[fid],
            "application_id": application_id, "patent_id": pid,
            "filing_date": date, "filing_year": year,
            "ownership_status": "unique_normalized_assignee_link",
        })

    apps = pd.DataFrame(app_rows)
    apps.to_csv(REC / "recovered_granted_application_links_all_candidates.csv", index=False, encoding="utf-8-sig")
    usable = apps[apps.ownership_status.eq("unique_normalized_assignee_link")].copy()
    usable = usable.sort_values(["full_firm_id", "application_id", "patent_id"]).drop_duplicates(
        ["full_firm_id", "application_id"]
    )
    usable.to_csv(REC / "recovered_granted_application_level_unique.csv", index=False, encoding="utf-8-sig")

    ref = firms[["full_firm_id", "reference_year"]].copy()
    usable = usable.merge(ref, on="full_firm_id", how="left", validate="many_to_one")
    at_ref = usable[usable.filing_year.le(usable.reference_year)].groupby("full_firm_id").application_id.nunique()
    firms["granted_application_count_at_reference"] = firms.full_firm_id.map(at_ref).fillna(0).astype(int)
    firms["pre_vd_granted_application_count"] = firms["granted_application_count_at_reference"]
    firms.to_csv(REC / "full7316_matching_covariates_with_recovered_patent_count.csv", index=False, encoding="utf-8-sig")
    firms.to_stata(REC / "full7316_matching_covariates_with_recovered_patent_count.dta", write_index=False, version=118)

    print({
        "firms": int(firms.full_firm_id.nunique()),
        "candidate_application_rows": int(len(apps)),
        "unique_linked_applications": int(usable.application_id.nunique()),
        "firms_with_granted_application": int(usable.full_firm_id.nunique()),
        "multi_firm_collision_rows": int(apps.ownership_status.eq("multi_firm_name_collision").sum()),
    })


if __name__ == "__main__":
    main()
