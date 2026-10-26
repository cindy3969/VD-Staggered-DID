import json
from pathlib import Path

roots = [
    Path(r"C:\Users\user\.codex\sessions\2026\09"),
    Path(r"C:\Users\user\.codex\sessions\2026\10"),
]
needles = [
    "-0.226", "-.226", "-0.190", "-.190", "88,547", "88547",
    "Aggregated event study ATT", "Table 1. Staggered",
    "count_granted_treated_control_trajectories",
    "Table_CS_verified.do", "ATT_numeric.csv", "csdid_all.ster",
]

def strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from strings(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from strings(value)

hits = []
for root in roots:
    if not root.exists():
        continue
    for path in root.rglob("*.jsonl"):
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            for line_no, line in enumerate(fh, 1):
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                for value in strings(obj):
                    low = value.lower()
                    matched = [n for n in needles if n.lower() in low]
                    if not matched:
                        continue
                    positions = [low.find(n.lower()) for n in matched if low.find(n.lower()) >= 0]
                    pos = min(positions)
                    span_before = 12000 if "table_cs_verified.do" in low else 1200
                    span_after = 24000 if "table_cs_verified.do" in low else 4000
                    excerpt = value[max(0, pos - span_before): pos + span_after]
                    hits.append((str(path), line_no, obj.get("timestamp", ""), matched, excerpt))
                    break

out = Path(r"C:\Users\user\Documents\VD\outputs\patent_panel_recovery\historical_csdid_hits.txt")
with out.open("w", encoding="utf-8") as fh:
    for path, line_no, timestamp, matched, excerpt in hits:
        fh.write("=" * 100 + "\n")
        fh.write(f"{path}:{line_no}  {timestamp}  MATCH={matched}\n")
        fh.write(excerpt.replace("\\r\\n", "\n") + "\n")
print(f"wrote {len(hits)} hits to {out}")
