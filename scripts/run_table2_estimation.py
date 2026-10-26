from pathlib import Path
import json
import subprocess
import sys
import time

ROOT = Path(r"C:\Users\user\Documents\VD")
OUT = ROOT / "outputs" / "table2_forward_citations_application_level"
PY = Path(r"C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")
subs = ["all", "noprior", "prior", "early", "late"]

jobs = [[s, "forward_citations_adjusted_mean", "never", 2024, True, 49, 20261013] for s in subs]
running = []
for i, job in enumerate(jobs):
    log = open(OUT / f"table2_boot_{i}.log", "w", encoding="utf-8")
    proc = subprocess.Popen(
        [str(PY), "dripw_table2.py", json.dumps([job]), f"table2_boot_{i}.csv"],
        cwd=OUT, stdout=log, stderr=subprocess.STDOUT,
    )
    running.append((proc, log))
for proc, log in running:
    proc.wait()
    log.close()
    if proc.returncode:
        raise SystemExit(f"Estimator failed with return code {proc.returncode}")

# Raw citations are a non-bootstrapped sensitivity result.
raw_jobs = [[s, "forward_citations_raw_mean", "never", 2024, True, 0, 20261013] for s in subs]
subprocess.run(
    [str(PY), "dripw_table2.py", json.dumps(raw_jobs), "table2_raw_sensitivity.csv"],
    cwd=OUT, check=True,
)

