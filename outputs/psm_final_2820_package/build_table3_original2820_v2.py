"""Rebuild the requested outcomes on the ORIGINAL 260122 sample, without PSM.

Uses the definitions in build_current_table3_cross_section.py. Never overwrites
the original sample or the rematched data. Stata merges the new columns so all
original values, labels, formats and treatment assignments are retained.
"""
from pathlib import Path
import json
import re
import subprocess
import tempfile
import numpy as np
import pandas as pd

ROOT = Path('C:/Users/user/Documents/VD')
PKG = ROOT / 'outputs/psm_final_2820_package'
SOURCE = Path('C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms/260122 winsorization.dta')
TARGET = PKG / 'table3_original_2820_cross_section_v2.dta'
STATA = 'C:/Program Files/StataNow19/StataSE-64.exe'
key = lambda value: re.sub(r'[^a-z0-9]', '', str(value).lower())
old = pd.read_stata(SOURCE, convert_categoricals=False)
assert len(old) == 2820 and old.firm_id.is_unique
assert old.VD.value_counts().to_dict() == {0: 1410, 1: 1410}
assert old.VDyear.equals(old.VDYear)
ref = old[['firm_id', 'OrganizationName', 'VDyear']].copy()
ref['name_key'] = ref.OrganizationName.map(key)
assert ref.name_key.is_unique
roster = pd.read_stata(ROOT / 'outputs/csdid_ultimately_granted_primary/csdid_ultimately_granted_full7316_controls.dta', convert_categoricals=False)
assert ref.name_key.isin(roster.organization_name.map(key)).all()

apps = pd.read_csv(ROOT / 'outputs/csdid_union_corrected_3yr/application_level_union_corrected_visible_mismatches.csv', dtype={'application_id': str}, low_memory=False)
apps = apps.loc[apps.filing_year.between(2010, 2024)].copy()
assert not apps[['full_firm_id', 'application_id']].duplicated().any()
assert len(apps) == 39249
apps['name_key'] = apps.organization_name.map(key)
assert not apps[['name_key', 'full_firm_id']].drop_duplicates().name_key.duplicated().any()
rates = apps.groupby('filing_year').ultimately_granted.mean()
assert rates.gt(0).all()
apps['granted_normalized'] = apps.ultimately_granted / apps.filing_year.map(rates)

methods = pd.read_csv(ROOT / 'outputs/table2_forward_citation_year_methods_39249/application_level_with_forward_citation_methods.csv', usecols=['full_firm_id', 'application_id', 'filing_year', 'fwd_raw_total'], dtype={'application_id': str})
assert len(methods) == 39249
cpc = pd.read_csv(ROOT / 'outputs/table2_forward_citation_year_methods_39249/application_citation_year_grid.csv', usecols=['application_id', 'cpc3'], dtype={'application_id': str})
assert cpc.groupby('application_id').cpc3.nunique().le(1).all()
cpc = cpc.drop_duplicates('application_id')
methods = methods.merge(cpc, on='application_id', how='left', validate='one_to_one')
denom = methods.groupby(['filing_year', 'cpc3'], dropna=False).fwd_raw_total.transform('mean')
methods['adjusted_citation_v4'] = np.where(denom.gt(0), methods.fwd_raw_total / denom, 0.0)
apps = apps.merge(methods[['full_firm_id', 'application_id', 'adjusted_citation_v4']], on=['full_firm_id', 'application_id'], how='left', validate='one_to_one', indicator=True)
assert apps['_merge'].eq('both').all()
assert apps.adjusted_citation_v4.notna().all()
apps = apps.drop(columns='_merge').merge(ref, on='name_key', how='inner', validate='many_to_one')
window = apps.loc[(apps.filing_year - apps.VDyear).between(1, 3)]
totals = window.groupby('firm_id').agg(
    grantedpatentbyfiling_win3=('ultimately_granted', 'sum'),
    grantedpatentbyfiling_norm_win3=('granted_normalized', 'sum'),
    adjusted_citation_total=('adjusted_citation_v4', 'sum'))
new = ref.merge(totals, on='firm_id', how='left', validate='one_to_one')
for col in ['grantedpatentbyfiling_win3', 'grantedpatentbyfiling_norm_win3', 'adjusted_citation_total']:
    new[col] = new[col].fillna(0)
new['norm_cite_perpat_win3_v4'] = new.adjusted_citation_total / new.grantedpatentbyfiling_win3.replace(0, np.nan)
new['win3_complete_2024'] = (new.VDyear + 3 <= 2024).astype('int8')
cols = ['grantedpatentbyfiling_win3', 'grantedpatentbyfiling_norm_win3', 'norm_cite_perpat_win3_v4']
current = pd.read_stata(PKG / 'table3_current_2820_cross_section_v2.dta', convert_categoricals=False)
shared = new.merge(current[['OrganizationName', 'VDyear'] + cols], on='OrganizationName', suffixes=('_new', '_current'), validate='one_to_one')
same_reference = shared.loc[shared.VDyear_new.eq(shared.VDyear_current)]
comparisons = {}
for col in cols:
    equal = np.isclose(same_reference[col+'_new'], same_reference[col+'_current'], rtol=1e-7, atol=1e-9, equal_nan=True)
    comparisons[col] = {'compared': len(equal), 'equal': int(equal.sum())}
    assert equal.all(), (col, same_reference.loc[~equal, ['OrganizationName', col+'_new', col+'_current']].head(15))

# Keep all legacy columns verbatim. Do not apply fresh winsorization or recode
# undefined quality as zero. The citation v4 source is retained, not replaced by
# a different citation-window variable from later robustness exercises.
with tempfile.TemporaryDirectory(prefix='vd_original2820_') as tmp:
    tmp = Path(tmp)
    supplement = tmp / 'outcomes.dta'
    new[['firm_id'] + cols + ['win3_complete_2024']].to_stata(supplement, write_index=False, version=118)
    build = tmp / 'merge.do'
    build.write_text('''version 19
clear all
set more off
log using "''' + (tmp / 'merge.log').as_posix() + '''", text replace
use "''' + SOURCE.as_posix() + '''", clear
merge 1:1 firm_id using "''' + supplement.as_posix() + '''", assert(match) nogen
assert _N == 2820
label variable grantedpatentbyfiling_win3 "Ultimately granted applications filed t+1 to t+3"
label variable grantedpatentbyfiling_norm_win3 "Granted applications t+1 to t+3 / filing-year grant rate"
label variable norm_cite_perpat_win3_v4 "Filing-year x CPC3 normalized citations per granted application t+1..t+3"
label variable win3_complete_2024 "Reference year + 3 <= 2024; full outcome window observed"
generate double ln_grantedbyfiling_win3 = log(grantedpatentbyfiling_win3+1)
generate double ln_grantedbyfiling_norm_win3 = log(grantedpatentbyfiling_norm_win3+1)
generate double ln_norm_cite_perpat_win3_v4 = log(norm_cite_perpat_win3_v4+1)
generate byte Priorpatent_VD = patentdummybyfiling
generate byte nopriorpatentdummy_VD = 1-patentdummybyfiling
generate byte Earlystage_VD = earlystage
notes: Original 2820 firms and all original controls from 260122 winsorization.dta; no rematching.
notes: Outcomes use filing years VDyear+1 through VDyear+3 and source coverage through 2024.
notes: Grant-rate normalization is cohort scaling, not a fully identified censoring correction.
notes: Citation v4 preserves the existing v4 definition/source; undefined with zero granted patents.
notes: win3_complete_2024 flags incomplete follow-up. No automatic sample exclusion or new winsorization.
sort firm_id
save "''' + TARGET.as_posix() + '''", replace
log close
exit, clear
''', encoding='utf-8')
    result = subprocess.run([STATA, '/e', 'do', str(build)], creationflags=subprocess.CREATE_NO_WINDOW, timeout=180)
    log = (tmp / 'merge.log').read_text(encoding='utf-8', errors='replace')
    assert TARGET.exists() and 'saved' in log, log
    assert not re.search(r'^r\(\d+\);', log, re.M), log

saved = pd.read_stata(TARGET, convert_categoricals=False).sort_values('firm_id').reset_index(drop=True)
expected = old.sort_values('firm_id').reset_index(drop=True)
pd.testing.assert_frame_equal(saved[old.columns], expected, check_dtype=False, check_exact=True)
assert pd.io.stata.StataReader(SOURCE).value_labels() == {k:v for k,v in pd.io.stata.StataReader(TARGET).value_labels().items() if k in pd.io.stata.StataReader(SOURCE).value_labels()}
audit = {
    'source': str(SOURCE), 'output': str(TARGET), 'firms': len(saved),
    'treated': int(saved.VD.sum()), 'controls': int((saved.VD == 0).sum()),
    'original_columns_preserved_exactly': len(old.columns),
    'shared_with_rematched': len(shared), 'same_reference_year': len(same_reference),
    'shared_outcome_verification': comparisons,
    'quality_nonmissing': int(saved.norm_cite_perpat_win3_v4.notna().sum()),
    'incomplete_3year_windows': int((saved.win3_complete_2024 == 0).sum()),
    'outcome_sums': saved[cols[:2]].sum().to_dict(),
    'normalization': 'Same existing 39249-application universe; no change of definition',
}
(PKG / 'table3_original2820_v2_QA.json').write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(audit, indent=2, ensure_ascii=False))
