import json
from pathlib import Path

src=Path(r"C:\Users\user\.codex\sessions\2026\09\12\rollout-2026-09-12T22-59-19-01a095ea-5d92-7503-9a68-e522c6efa4af.jsonl")
out=Path(r"C:\Users\user\Documents\VD\outputs\patent_panel_recovery\session_calls_application_linkage.txt")
needles=("full_cohort_application_level_linked_through_2024", "unique_A1_applications", "6319", "10727", "dual_application_counts_2024", "application_level_list_verified_legal_aliases", "apply_verified_legal_alias_applications", "full_cohort_pgpub_A1_links_2024")
blocks=[]
for line in src.open(encoding="utf-8"):
    try: obj=json.loads(line)
    except Exception: continue
    payload=obj.get("payload",{})
    if payload.get("type")!="custom_tool_call": continue
    s=str(payload.get("input", ""))
    if any(n in s for n in needles):
        blocks.append(f"\n\n===== ordinal {obj.get('ordinal')} name={payload.get('name')} =====\n{s}")
out.write_text("".join(blocks),encoding="utf-8")
print(out, len(blocks), out.stat().st_size)
