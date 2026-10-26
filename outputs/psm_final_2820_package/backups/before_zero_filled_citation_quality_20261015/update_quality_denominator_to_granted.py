from pathlib import Path

import pandas as pd


PKG = Path(r"C:\Users\user\Documents\VD\outputs\psm_final_2820_package")
STAGE = PKG / "table3_granted_denominator_stage"
CURRENT = PKG / "table3_current_2820_cross_section"
V2 = PKG / "table3_current_2820_cross_section_v2"

stage = pd.read_csv(STAGE.with_suffix(".csv"), low_memory=False)
old_v2 = pd.read_csv(V2.with_suffix(".csv"), low_memory=False)
assert len(stage) == 2820 and stage["firm_id"].is_unique
assert len(old_v2) == 2820 and old_v2["firm_id"].is_unique

# Preserve every V2-only variable while replacing all common variables with
# the reproducibly rebuilt values from the granted-patent denominator build.
extra_cols = [c for c in old_v2.columns if c not in stage.columns]
v2 = stage.merge(old_v2[["firm_id"] + extra_cols], on="firm_id", how="left",
                 validate="one_to_one")
v2 = v2[[c for c in old_v2.columns if c in v2.columns]]
assert len(v2) == 2820

# Restore the category labels embedded in the staged Stata file.
stage_codes = pd.read_stata(STAGE.with_suffix(".dta"), convert_categoricals=False)
stage_labels = pd.read_stata(STAGE.with_suffix(".dta"), convert_categoricals=True)
value_labels = {}
for variable in ["Region2", "Industry2"]:
    pairs = pd.DataFrame({
        "code": stage_codes[variable].astype(int),
        "label": stage_labels[variable].astype(str),
    }).drop_duplicates()
    assert pairs["code"].is_unique
    value_labels[variable] = dict(zip(pairs["code"], pairs["label"]))

variable_labels = {
    "Region2": "Region category (source Region2)",
    "Industry2": "Industry category (source Industry2)",
    "norm_cite_perpat_win3_v1": "Citation quality per granted patent t+1 to t+3: filing cohort",
    "norm_cite_perpat_win3_v2": "Citation quality per granted patent t+1 to t+3: filing cohort and CPC3",
    "norm_cite_perpat_win3_v3": "Citation quality per granted patent t+1 to t+3: exposure-adjusted rate",
    "norm_cite_perpat_win3_v4": "Citation quality per granted patent t+1 to t+3: filing year and CPC3",
}

stage.to_csv(CURRENT.with_suffix(".csv"), index=False, encoding="utf-8-sig")
stage.to_stata(CURRENT.with_suffix(".dta"), write_index=False, version=118,
               value_labels=value_labels, variable_labels=variable_labels)
v2.to_csv(V2.with_suffix(".csv"), index=False, encoding="utf-8-sig")
v2.to_stata(V2.with_suffix(".dta"), write_index=False, version=118,
            value_labels=value_labels, variable_labels=variable_labels)

quality = [f"norm_cite_perpat_win3_v{i}" for i in range(1, 5)]
for name, frame in [("current", stage), ("v2", v2)]:
    zero = frame["grantedpatentbyfiling_win3"].eq(0)
    assert frame.loc[zero, quality].isna().all().all()
    assert frame.loc[~zero, quality].notna().all().all()
    print(name, len(frame), len(frame.columns), int(zero.sum()), extra_cols)
