from pathlib import Path
from datetime import datetime
import shutil
import pandas as pd

root = Path(__file__).resolve().parents[1] / 'outputs' / 'psm_final_2820_package'
source = root / 'table3_current_2820_cross_section_v2.dta'
target = source.with_suffix('.csv')
data = pd.read_stata(source, convert_categoricals=False)
old = pd.read_csv(target)
assert len(data) == len(old) == 2820
assert data.firm_id.is_unique and old.firm_id.is_unique
assert set(data.firm_id) == set(old.firm_id)
assert set(old.columns).issubset(data.columns)
pd.testing.assert_frame_equal(
    data.set_index('firm_id')[old.columns.drop('firm_id')].sort_index(),
    old.set_index('firm_id').sort_index(),
    check_dtype=False, check_index_type=False, check_exact=False, rtol=1e-12, atol=1e-12,
)
backup = root / 'backups' / ('before_csv_status_sync_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
backup.mkdir(parents=True, exist_ok=False)
shutil.copy2(target, backup / target.name)
staged = target.with_suffix('.sync.tmp.csv')
data.to_csv(staged, index=False, encoding='utf-8-sig')
check = pd.read_csv(staged, keep_default_na=False)
assert list(check.columns) == list(data.columns)
assert len(check) == len(data)
for col in ['status', 'm_a', 'ipo', 'defunct', 'status_date']:
    assert check[col].tolist() == data[col].tolist(), col
staged.replace(target)
print('Updated:', target)
print('Shape:', data.shape)
print('Added:', [col for col in data.columns if col not in old.columns])
print('Backup:', backup / target.name)
