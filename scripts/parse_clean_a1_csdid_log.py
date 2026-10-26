from pathlib import Path
import re
import pandas as pd

ROOT = Path(r"C:\Users\user\Documents\VD")
OUT = ROOT / "outputs" / "csdid_a1_clean_3yr"
text = (OUT / "MASTER_csdid_A1_3yr_title_dedup.log").read_text(encoding="utf-8", errors="replace")
number = r"[-+]?\.?\d+(?:\.\d+)?"
sections = re.compile(
    r"=== CLEAN_BEGIN outcome=(?P<outcome>\w+) sample=(?P<sample>\w+) ==="
    r"(?P<body>.*?)"
    r"=== CLEAN_END outcome=(?P=outcome) sample=(?P=sample) ===", re.S
)
rows = []
for m in sections.finditer(text):
    body = m.group("body")
    att = re.findall(rf"^\s*ATT \|\s+({number})\s+({number})\s+({number})\s+({number})", body, re.M)
    post = re.search(rf"^\s*Post_avg \|\s+({number})\s+({number})\s+({number})\s+({number})", body, re.M)
    obs = re.search(r"OBS=(\d+)", body)
    firms = re.search(r"FIRMS=(\d+)", body)
    if not att or not post:
        continue
    a = att[0]
    rows.append({
        "outcome": m.group("outcome"), "sample": m.group("sample"),
        "simple_att": float(a[0]), "simple_se": float(a[1]), "simple_p": float(a[3]),
        "event_post_avg": float(post.group(1)), "event_post_se": float(post.group(2)),
        "event_post_p": float(post.group(4)), "observations": int(obs.group(1)),
        "firms": int(firms.group(1)),
    })
df = pd.DataFrame(rows)
df.to_csv(OUT / "Table_clean_A1_3yr_title_dedup_results.csv", index=False)
print(df.to_string(index=False))
