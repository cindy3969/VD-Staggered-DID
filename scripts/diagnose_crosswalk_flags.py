import pandas as pd
import zipfile
from pathlib import Path

apps = pd.read_csv(
    r"outputs/patent_application_list_rebuilt_2024/patent_application_list_through_2024.csv",
    dtype=str,
)
target = set(apps.publication_patent_numbers.astype(str))
p = Path(r"outputs/patentsview_2024_full_cohort/source2024/pg_granted_pgpubs_crosswalk.tsv.zip")
parts = []
with zipfile.ZipFile(p) as z:
    with z.open(z.namelist()[0]) as f:
        for c in pd.read_csv(f, sep="\t", dtype=str, chunksize=1_000_000):
            h = c[c.pgpub_id.isin(target)]
            if len(h):
                parts.append(h)
x = pd.concat(parts, ignore_index=True)
print(x.columns.tolist())
print(x[["current_pgpub_id_flag", "current_patent_id_flag"]].value_counts(dropna=False))
print("apps all", x.application_id.nunique())
for a in ["1", "0"]:
    for b in ["1", "0"]:
        y = x[(x.current_pgpub_id_flag == a) & (x.current_patent_id_flag == b)]
        print(a, b, y.application_id.nunique())
print("both current", x[(x.current_pgpub_id_flag == "1") & (x.current_patent_id_flag == "1")].application_id.nunique())
cur = x[(x.current_pgpub_id_flag == "TRUE") & (x.current_patent_id_flag == "TRUE")]
old = x[(x.current_pgpub_id_flag == "FALSE") & (x.current_patent_id_flag == "TRUE")]
print("true/true unique apps", cur.application_id.nunique())
print("false/true unique apps", old.application_id.nunique())
print("false/true also true/true", old.application_id.isin(set(cur.application_id)).sum())
print("false/true app not true/true", old.loc[~old.application_id.isin(set(cur.application_id)), ["pgpub_id", "application_id", "patent_id"]].to_string(index=False))
