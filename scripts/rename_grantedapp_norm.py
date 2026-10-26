from pathlib import Path
import pandas as pd

root = Path(r'C:\Users\user\Documents\VD')
out = root / 'outputs/csdid_all_applications_corrected'
path = out / 'firm_year_all_applications_and_truncation_specs.dta'
with pd.read_stata(path, iterator=True, convert_categoricals=False) as reader:
    labels = reader.variable_labels()
    data = reader.read()
old = 'ug_rt_normalized'
new = 'grantedapp_norm'
assert old in data and new not in data
original = data[old].copy()
data.rename(columns={old: new}, inplace=True)
labels.pop(old, None)
labels[new] = 'Granted apps / filing-year observed grant rate; not full censoring correction'
data.to_stata(path, write_index=False, version=118, variable_labels=labels)
data.to_csv(path.with_suffix('.csv'), index=False)
check = pd.read_stata(path, convert_categoricals=False)
assert check[new].equals(original)
assert old not in check
for rel in ['scripts/add_rt_normalized_ug_outcome.py',
            'outputs/csdid_all_applications_corrected/MASTER_csdid_all_applications.do']:
    target = root / rel
    source = target.read_text(encoding='utf-8-sig')
    target.write_text(source.replace(old, new), encoding='utf-8')
print(f'Validated rename: {len(check):,} rows; values unchanged.')
