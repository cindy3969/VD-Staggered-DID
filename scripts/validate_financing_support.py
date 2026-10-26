from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parents[1]
out = root / "outputs/downstream_financing"
pkg = root / "outputs/psm_final_2820_package"
text = (pkg / "RUN_TABLE3_PATENT_APPLICATION_WIN3_v2.do").read_text(encoding="utf-8-sig")
block = text.split("* DOWNSTREAM_FINANCING_SUPPORT_20261020")[1].split("* Table 5:")[0]
code = f'''version 19
clear all
set more off
global ROOT "{pkg.as_posix()}"
global OUT "{out.as_posix()}"
log using "$OUT/validation.log", text replace
use "$ROOT/table3_original_2820_cross_section_v2.dta", clear
'''
(out / "validate.do").write_text(code + block + '\ndisplay "FINANCING_VALIDATION_COMPLETE"\nlog close\n', encoding="utf-8")
e = pd.read_stata(root / "outputs/table67_merge_audit/estimates.dta")
m = e[e.source.eq("legacy")].merge(e[e.source.eq("current")], on=["model", "term"], suffixes=("_old", "_current"))
for c in ["b", "se", "p", "N", "failures"]:
    a, b = m[c+"_old"], m[c+"_current"]
    assert (a.eq(b) | (a.isna() & b.isna())).all(), c
m.to_csv(out / "legacy_estimate_comparison.csv", index=False)
print("All legacy coefficients, standard errors, p-values, N and failures identical.")
