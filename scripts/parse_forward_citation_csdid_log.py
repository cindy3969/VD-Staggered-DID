from pathlib import Path
import re
import pandas as pd

root = Path(r"C:\Users\user\Documents\VD\outputs\table2_forward_citation_year_methods_39249")
logs = sorted(root.glob("csdid_fwd_*.log"))
text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in logs)
pattern = re.compile(
    r"=== BEGIN_SPEC outcome=(\S+) sample=(\S+) OBS_RAW=([0-9]+) ===(.*?)"
    r"=== END_SPEC outcome=\1 sample=\2 ===", re.S
)
rows = []
for outcome, sample, obs, block in pattern.findall(text):
    firms = re.search(r"FIRMS_RAW=([0-9]+)", block)
    atts = re.findall(r"^\s*ATT\s*\|\s*([-+.0-9eE]+)\s+([-+.0-9eE]+)\s+[-+.0-9eE]+\s+([0-9.]+)", block, re.M)
    post = re.search(r"^\s*Post_avg\s*\|\s*([-+.0-9eE]+)\s+([-+.0-9eE]+)\s+[-+.0-9eE]+\s+([0-9.]+)", block, re.M)
    simple, simple_se, simple_p = map(float, atts[-1]) if atts else (float("nan"),) * 3
    post_att, post_se, post_p = map(float, post.groups()) if post else (float("nan"),) * 3
    rows.append({
        "outcome": outcome, "sample": sample,
        "simple_att": simple, "simple_se": simple_se, "simple_p": simple_p,
        "event_post_avg_att": post_att, "event_post_avg_se": post_se, "event_post_avg_p": post_p,
        "observations": int(obs), "firms": int(firms.group(1)) if firms else None,
    })
result = pd.DataFrame(rows)
result.to_csv(root / "Table2_all_truncation_methods_results.csv", index=False, encoding="utf-8-sig")
print(result.to_string(index=False))
