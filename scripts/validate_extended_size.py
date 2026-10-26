from pathlib import Path
import pandas as pd
import numpy as np
B=Path(__file__).resolve().parents[1]/'outputs/psm_final_2820_package'
O=B/'postvd_size_research'
d=pd.read_stata(B/'table3_current_2820_cross_section_v2.dta',convert_categoricals=False)
c=pd.read_csv(B/'table3_current_2820_cross_section_v2.csv',keep_default_na=False)
b=pd.read_stata(B/'backups/before_extended_size_20261020_100745/table3_current_2820_cross_section_v2.dta',convert_categoricals=False)
assert len(d)==2820 and d.firm_id.is_unique
for col in b:
    if not col.startswith(('employees_','revenue_')):
        pd.testing.assert_series_equal(d[col],b[col])
ds=d.sort_values('firm_id').reset_index(drop=True)
cs=c.sort_values('firm_id').reset_index(drop=True)
assert set(ds)-set(cs)=={'numberofvddeals','vdsupply'}
assert set(cs)-set(ds)=={'Region2_label','Industry2_label'}
for col in set(ds)&set(cs):
    if pd.api.types.is_numeric_dtype(ds[col]):
        np.testing.assert_allclose(ds[col],pd.to_numeric(cs[col],errors='coerce'),equal_nan=True)
    else: assert ds[col].fillna('').astype(str).tolist()==cs[col].astype(str).tolist(),col
p=pd.read_stata(O/'postvd_size_all_years.dta',convert_categoricals=False)
assert not p.duplicated(['firm_id','year']).any()
assert (p.t.eq(p.year-p.VDyear)&p.t.gt(0)).all()
for metric,val in [('employees','employees'),('revenue','revenue_usd')]:
    observed=d[f'{metric}_post'].notna()
    assert d.loc[observed,f'{metric}_post_t'].gt(0).all()
    g=p[p[val].notna()].sort_values('year').drop_duplicates('firm_id').set_index('firm_id')
    np.testing.assert_allclose(d.loc[observed,f'{metric}_post'],d.loc[observed,'firm_id'].map(g[val]))
    assert int(d[f'{metric}_post_nyears'].sum())==p[val].notna().sum()
    for t in (1,2,3):
        g=p[p.t.eq(t)].set_index('firm_id')
        np.testing.assert_allclose(d[f'{metric}_t{t}'],d.firm_id.map(g[val]),equal_nan=True)
print('PASS: 2820 identities, all unrelated fields preserved, CSV/DTA equality, unique firm-years, valid timing, earliest values and all t1-t3 outcomes reconciled.')
