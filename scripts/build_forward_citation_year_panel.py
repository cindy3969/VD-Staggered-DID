"""Build application-year and firm-year forward-citation outcomes.

Primary inputs are the retained application list used in the earlier Table 1
replication and PatentsView citation/CPC bulk files.  The build deliberately
keeps zero-citation application-years in all cohort denominators.
"""
from pathlib import Path
import json
import re
import zipfile

import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\user\Documents\VD")
OUT = ROOT / "outputs" / "table2_forward_citation_year_methods_39249"
OUT.mkdir(parents=True, exist_ok=True)
APP_FILE = ROOT / "outputs" / "csdid_union_corrected_3yr" / "application_level_union_corrected_visible_mismatches.csv"
BASE_PANEL = ROOT / "outputs" / "csdid_historical_replication_verified" / "MASTER_CS_TABLE_restored.dta"
PV = ROOT / "outputs" / "patentsview_2024_full_cohort" / "source"
CITATION_ZIP = PV / "g_us_patent_citation.tsv.zip"
CPC_ZIP = PV / "g_cpc_current.tsv.zip"
CUTOFF_YEAR = 2024


def zip_member(path: Path):
    archive = zipfile.ZipFile(path)
    member = next(name for name in archive.namelist() if not name.endswith("/"))
    return archive, archive.open(member)


def clean_patent_id(value):
    if pd.isna(value):
        return None
    digits = re.sub(r"\D", "", str(value).split(".")[0])
    return int(digits) if digits else None


def explode_grants(apps):
    rows = []
    for row in apps.itertuples(index=False):
        grant_date = pd.to_datetime(getattr(row, "first_grant_date", None), errors="coerce")
        if pd.isna(grant_date):
            grant_year = pd.to_numeric(getattr(row, "grant_year_used", None), errors="coerce")
            if pd.isna(grant_year):
                grant_year = pd.to_numeric(getattr(row, "legacy_first_grant_year", None), errors="coerce")
            if pd.notna(grant_year):
                grant_date = pd.Timestamp(year=int(grant_year), month=1, day=1)
        ids = []
        for field in [getattr(row, "grant_patent_ids", None), getattr(row, "legacy_grant_patent_ids", None)]:
            if pd.isna(field):
                continue
            ids.extend(clean_patent_id(token) for token in re.split(r"[;|, ]+", str(field)) if token)
        ids = list(dict.fromkeys(x for x in ids if x))
        for pid in ids:
            rows.append((str(row.application_id), int(row.full_firm_id), int(row.filing_year),
                         grant_date, pid))
    return pd.DataFrame(rows, columns=["application_id", "full_firm_id", "filing_year", "grant_date", "patent_id"])


def read_citations(target_ids):
    archive, stream = zip_member(CITATION_ZIP)
    try:
        header = pd.read_csv(stream, sep="\t", nrows=0).columns.tolist()
    finally:
        stream.close(); archive.close()
    cited_col = next(c for c in ["citation_patent_id", "cited_patent_id"] if c in header)
    citing_col = next(c for c in ["patent_id", "citing_patent_id"] if c in header)
    date_col = next((c for c in ["citation_date", "patent_date", "citing_patent_date"] if c in header), None)
    if date_col is None:
        raise RuntimeError(f"No citation date column in {header}")
    pieces = []
    archive, stream = zip_member(CITATION_ZIP)
    try:
        for chunk in pd.read_csv(stream, sep="\t", usecols=[cited_col, citing_col, date_col], dtype="string", chunksize=1_500_000):
            cited = pd.to_numeric(chunk[cited_col], errors="coerce")
            keep = cited.isin(target_ids) & chunk[date_col].notna()
            if keep.any():
                x = chunk.loc[keep, [cited_col, citing_col, date_col]].copy()
                x.columns = ["patent_id", "citing_patent_id", "citation_date"]
                x["patent_id"] = pd.to_numeric(x.patent_id, errors="coerce").astype("Int64")
                x["citation_date"] = pd.to_datetime(x.citation_date, errors="coerce")
                pieces.append(x.dropna(subset=["patent_id", "citation_date"]))
    finally:
        stream.close(); archive.close()
    if not pieces:
        return pd.DataFrame(columns=["patent_id", "citing_patent_id", "citation_date"]), header
    return pd.concat(pieces, ignore_index=True).drop_duplicates(["patent_id", "citing_patent_id"]), header


def read_primary_cpc(target_ids):
    archive, stream = zip_member(CPC_ZIP)
    try:
        header = pd.read_csv(stream, sep="\t", nrows=0).columns.tolist()
    finally:
        stream.close(); archive.close()
    group_col = next(c for c in ["cpc_group_id", "cpc_subgroup_id", "cpc_class", "cpc_class_id"] if c in header)
    seq_col = next((c for c in ["cpc_sequence", "sequence"] if c in header), None)
    usecols = ["patent_id", group_col] + ([seq_col] if seq_col else [])
    pieces = []
    archive, stream = zip_member(CPC_ZIP)
    try:
        for chunk in pd.read_csv(stream, sep="\t", usecols=usecols, dtype="string", chunksize=1_500_000):
            pid = pd.to_numeric(chunk.patent_id, errors="coerce")
            x = chunk.loc[pid.isin(target_ids)].copy()
            if len(x): pieces.append(x)
    finally:
        stream.close(); archive.close()
    if not pieces:
        return pd.DataFrame(columns=["patent_id", "cpc3"]), header
    cpc = pd.concat(pieces, ignore_index=True)
    cpc["patent_id"] = pd.to_numeric(cpc.patent_id, errors="coerce").astype("Int64")
    if seq_col:
        cpc["_seq"] = pd.to_numeric(cpc[seq_col], errors="coerce").fillna(999999)
        cpc = cpc.sort_values(["patent_id", "_seq"])
    cpc["cpc3"] = cpc[group_col].fillna("").str.upper().str.extract(r"([A-HY]\d{2})", expand=False)
    return cpc.dropna(subset=["patent_id", "cpc3"]).drop_duplicates("patent_id")[["patent_id", "cpc3"]], header


def main():
    apps = pd.read_csv(APP_FILE, dtype={"application_id": "string"}, low_memory=False)
    apps["filing_year"] = pd.to_numeric(apps.filing_year, errors="coerce").astype("Int64")
    apps = apps.loc[apps.filing_year.between(2010, CUTOFF_YEAR)].drop_duplicates(
        ["full_firm_id", "application_id"], keep="first"
    ).copy()
    if len(apps) != 39249:
        raise RuntimeError(f"Expected 39,249 corrected analysis applications, found {len(apps):,}")
    grants = explode_grants(apps.loc[apps.ultimately_granted.eq(1)].copy())
    target_ids = set(grants.patent_id.astype(int))
    citations, citation_header = read_citations(target_ids)
    cpc, cpc_header = read_primary_cpc(target_ids)
    grants = grants.merge(cpc, on="patent_id", how="left")
    app_meta = grants.sort_values(["application_id", "grant_date", "patent_id"]).groupby("application_id", as_index=False).agg(
        full_firm_id=("full_firm_id", "first"), filing_year=("filing_year", "first"),
        grant_date=("grant_date", "min"), cpc3=("cpc3", "first"), grant_patent_count=("patent_id", "nunique")
    )
    citations = citations.merge(grants[["application_id", "patent_id", "grant_date"]], on="patent_id", how="inner")
    citations = citations[citations.citation_date.ge(citations.grant_date) | citations.grant_date.isna()].copy()
    citations["citation_year"] = citations.citation_date.dt.year.astype(int)
    citations = citations[citations.citation_year.le(CUTOFF_YEAR)]
    counts = citations.groupby(["application_id", "citation_year"], as_index=False).agg(
        n_cites=("citing_patent_id", "nunique")
    )

    # Complete application x calendar-year grid from filing year through cutoff.
    grid_rows = []
    for row in app_meta.itertuples(index=False):
        start = max(1900, int(row.filing_year))
        for year in range(start, CUTOFF_YEAR + 1):
            grid_rows.append((row.application_id, int(row.full_firm_id), int(row.filing_year),
                              row.grant_date, row.cpc3, int(row.grant_patent_count), year))
    grid = pd.DataFrame(grid_rows, columns=["application_id", "full_firm_id", "filing_year", "grant_date", "cpc3", "grant_patent_count", "year"])
    grid = grid.merge(counts, left_on=["application_id", "year"], right_on=["application_id", "citation_year"], how="left").drop(columns="citation_year")
    grid["n_cites"] = grid.n_cites.fillna(0).astype(int)
    grid["grant_year"] = grid.grant_date.dt.year
    grid["exposure_years"] = (grid.year - grid.grant_year + 1).clip(lower=1)
    grid.loc[grid.year.lt(grid.grant_year), "exposure_years"] = np.nan
    grid["cum_cites"] = grid.groupby("application_id").n_cites.cumsum()
    grid["annualized_rate"] = np.where(grid.year.ge(grid.grant_year), grid.cum_cites / grid.exposure_years, 0.0)

    # Filing-cohort x citation-year denominators. Zeros are present by construction.
    grid["cohort_mean"] = grid.groupby(["filing_year", "year"]).n_cites.transform("mean")
    grid["fwd_norm"] = np.where(grid.cohort_mean.gt(0), grid.n_cites / grid.cohort_mean, 0.0)
    grid["rate_mean"] = grid.groupby(["filing_year", "year"]).annualized_rate.transform("mean")
    grid["rate_norm"] = np.where(grid.rate_mean.gt(0), grid.annualized_rate / grid.rate_mean, 0.0)

    valid_cpc = grid.cpc3.notna()
    grid["cohort_mean_cpc"] = np.nan
    grid.loc[valid_cpc, "cohort_mean_cpc"] = grid.loc[valid_cpc].groupby(["filing_year", "year", "cpc3"]).n_cites.transform("mean")
    grid["fwd_norm_cpc"] = np.where(grid.cohort_mean_cpc.gt(0), grid.n_cites / grid.cohort_mean_cpc, np.nan)
    grid["rate_mean_cpc"] = np.nan
    grid.loc[valid_cpc, "rate_mean_cpc"] = grid.loc[valid_cpc].groupby(["filing_year", "year", "cpc3"]).annualized_rate.transform("mean")
    grid["rate_norm_cpc"] = np.where(grid.rate_mean_cpc.gt(0), grid.annualized_rate / grid.rate_mean_cpc, np.nan)
    grid.to_csv(OUT / "application_citation_year_grid.csv", index=False, encoding="utf-8-sig")

    firm_year = grid.groupby(["full_firm_id", "year"], as_index=False).agg(
        fwd_raw=("n_cites", "sum"),
        fwd_norm_cohort=("fwd_norm", "sum"),
        fwd_norm_cohort_cpc=("fwd_norm_cpc", "sum"),
        fwd_rate=("annualized_rate", "sum"),
        fwd_rate_norm=("rate_norm", "sum"),
        fwd_rate_norm_cpc=("rate_norm_cpc", "sum"),
        active_granted_apps=("application_id", "nunique"),
        cpc_covered_apps=("cpc3", "count"),
    )
    firm_year["fwd_cites_per_app"] = firm_year.fwd_raw / firm_year.active_granted_apps.replace(0, np.nan)
    firm_year["cpc_coverage"] = firm_year.cpc_covered_apps / firm_year.active_granted_apps.replace(0, np.nan)
    firm_year.to_csv(OUT / "forward_citations_firm_year_build.csv", index=False, encoding="utf-8-sig")

    panel = pd.read_stata(BASE_PANEL)
    old_outcomes = [c for c in panel.columns if c.startswith("fwd_") or c.startswith("cite_")]
    panel = panel.drop(columns=old_outcomes, errors="ignore").merge(firm_year, on=["full_firm_id", "year"], how="left", validate="one_to_one")
    outcome_cols = ["fwd_raw", "fwd_norm_cohort", "fwd_norm_cohort_cpc", "fwd_rate", "fwd_rate_norm", "fwd_rate_norm_cpc", "active_granted_apps", "cpc_covered_apps"]
    panel[outcome_cols] = panel[outcome_cols].fillna(0)
    panel["cpc_coverage"] = panel.cpc_coverage.fillna(1)
    for col in ["fwd_raw", "fwd_norm_cohort", "fwd_norm_cohort_cpc", "fwd_rate", "fwd_rate_norm", "fwd_rate_norm_cpc"]:
        panel["ln1p_" + col] = np.log1p(panel[col])
    panel.to_csv(OUT / "firm_year_with_citations.csv", index=False, encoding="utf-8-sig")
    dta = panel.copy()
    for col in dta.select_dtypes(include=["object", "string"]).columns:
        dta[col] = dta[col].fillna("").astype(str)
    dta.to_stata(OUT / "firm_year_with_citations.dta", write_index=False, version=118)

    app_summary = grid.groupby("application_id", as_index=False).agg(
        fwd_raw_total=("n_cites", "sum"), fwd_norm_total=("fwd_norm", "sum"),
        fwd_norm_cpc_total=("fwd_norm_cpc", "sum"), fwd_rate_last=("annualized_rate", "last"),
        fwd_rate_norm_last=("rate_norm", "last"), fwd_rate_norm_cpc_last=("rate_norm_cpc", "last"),
    )
    app_output = apps.merge(app_summary, on="application_id", how="left")
    app_output.to_csv(
        OUT / "application_level_with_forward_citation_methods.csv", index=False, encoding="utf-8-sig"
    )
    old_total = pd.to_numeric(app_output.get("forward_citations_through_2024"), errors="coerce")
    new_total = pd.to_numeric(app_output.get("fwd_raw_total"), errors="coerce")
    comparable = old_total.notna() & new_total.notna()
    total_corr = float(old_total[comparable].corr(new_total[comparable])) if comparable.sum() > 1 else None
    qa = {
        "application_rows": int(len(apps)), "grant_link_rows": int(len(grants)),
        "grant_linked_applications": int(app_meta.application_id.nunique()),
        "target_grant_patents": int(len(target_ids)), "dated_valid_citation_links": int(len(citations)),
        "application_year_grid_rows": int(len(grid)), "cpc_covered_applications": int(app_meta.cpc3.notna().sum()),
        "panel_rows": int(len(panel)), "panel_firms": int(panel.full_firm_id.nunique()),
        "citation_cutoff_year": CUTOFF_YEAR,
        "citation_columns": citation_header, "cpc_columns": cpc_header,
        "legacy_cumulative_comparable_applications": int(comparable.sum()),
        "legacy_vs_rebuilt_total_correlation": total_corr,
        "legacy_total_citations": float(old_total[comparable].sum()),
        "rebuilt_total_citations": float(new_total[comparable].sum()),
        "zero_grid": "all grant-linked applications x filing_year..2024",
        "cpc_definition": "primary/current CPC first 3 characters",
    }
    (OUT / "QA_summary.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
