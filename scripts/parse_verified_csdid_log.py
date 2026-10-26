from pathlib import Path
import re
import pandas as pd

ROOT = Path(r"C:\Users\user\Documents\VD")
OUT = ROOT / "outputs" / "csdid_historical_replication_verified"
text = (OUT / "MASTER_replicate_Table1_Figure1.log").read_text(encoding="utf-8", errors="replace")

rows = []
pat = re.compile(
    r"=== TABLE1_BEGIN label=(?P<label>\w+) method=(?P<method>\w+) ==="
    r"(?P<body>.*?)"
    r"=== TABLE1_END label=(?P=label) method=(?P=method) ===",
    re.S,
)
num = r"[-+]?\.?\d+(?:\.\d+)?"
for m in pat.finditer(text):
    body = m.group("body")
    obs = int(re.search(r"OBS=(\d+)", body).group(1))
    firms = int(re.search(r"FIRMS=(\d+)", body).group(1))
    att_lines = re.findall(rf"^\s*ATT \|\s+({num})\s+({num})\s+({num})\s+({num})", body, re.M)
    post = re.search(rf"^\s*Post_avg \|\s+({num})\s+({num})\s+({num})\s+({num})", body, re.M)
    if not att_lines or not post:
        continue
    a = att_lines[0]
    rows.append({
        "sample": m.group("label"), "method": m.group("method"),
        "simple_att": float(a[0]), "simple_se": float(a[1]), "simple_p": float(a[3]),
        "event_post_avg": float(post.group(1)), "event_post_se": float(post.group(2)),
        "event_post_p": float(post.group(4)), "observations": obs, "firms": firms,
    })

df = pd.DataFrame(rows)
df.to_csv(OUT / "Table1_Stata_DRIPW_results.csv", index=False)
print(df.to_string(index=False))
