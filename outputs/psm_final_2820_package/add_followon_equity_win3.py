"""Append follow-on primary equity USD, reference calendar years +1..+3.

Run after any cross-sectional rebuild. Preserve each target's existing fields.
No qualifying round, or any qualifying round with undisclosed amount => missing.
"""
from pathlib import Path
from datetime import datetime
import re
import shutil
import sys
import numpy as np
import pandas as pd

PKG = Path(__file__).resolve().parent
SOURCE = Path('C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms/2010 2015 Crunchbase deals merged_v4.xlsx')
ALL_FINANCING = '--all-financing' in sys.argv
VAR = 'moneyraised_win3' if ALL_FINANCING else 'Follow_on_Equity_Raised_win3'
PREFIX = 'moneyraised' if ALL_FINANCING else 'equityraised'
DESCRIPTION = 'All financing' if ALL_FINANCING else 'Primary equity'
STEMS = ['table3_current_2820_cross_section', 'table3_current_2820_cross_section_v2']
def key(x):
    return re.sub('[^a-z0-9]', '', str(x).lower())

deals = pd.read_excel(SOURCE, header=1, usecols=['no','Organization Name', 'deal no',
    'Deal year','Announced Date','Funding Type','Money Raised Currency (in USD)'])
deals['name_key'] = deals['Organization Name'].map(key)
deals['year'] = pd.to_numeric(deals['Deal year'], errors='raise')
deals['amount'] = pd.to_numeric(deals['Money Raised Currency (in USD)'], errors='coerce')
types = deals['Funding Type'].fillna('').str.strip()
deals['equity'] = types.isin(['Seed','Pre-Seed','Angel','Venture - Series Unknown',
    'Private Equity','Corporate Round','Equity Crowdfunding','Post-IPO Equity']) | types.str.match(r'^Series [A-I](?:\d+)?$')
backup = PKG/'backups'/('before_'+PREFIX+'_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir(parents=True)
audit_parts = []
for stem in STEMS:
    csv_path, dta_path = PKG/(stem+'.csv'), PKG/(stem+'.dta')
    old = pd.read_csv(csv_path)
    with pd.io.stata.StataReader(dta_path, convert_categoricals=False) as reader:
        labels = reader.variable_labels()
        value_labels = reader.value_labels()
        dta = reader.read()
    assert old.firm_id.is_unique and dta.firm_id.is_unique
    assert old.firm_id.tolist() == dta.firm_id.tolist()
    ref = old[['firm_id','OrganizationName','VDyear']].copy()
    ref['name_key'] = ref.OrganizationName.map(key)
    assert ref.name_key.is_unique
    assert ref.name_key.isin(deals.name_key).all(), 'Source firms missing'
    window = ref.merge(deals, on='name_key', how='left', validate='one_to_many')
    window = window.loc[window.year.sub(window.VDyear).between(1,3) & (True if ALL_FINANCING else window.equity)].copy()
    # Deal numbers identify distinct rounds. Do not deduplicate merely by date/amount.
    assert not window.duplicated(['firm_id','deal no']).any(), 'Repeated source deal identifiers'
    assert window.amount.dropna().ge(0).all()
    agg = window.groupby('firm_id').agg(rounds=('equity','size'), disclosed=('amount','count'), total=('amount',lambda x:x.sum(min_count=1)))
    agg.loc[agg.rounds.ne(agg.disclosed),'total'] = np.nan
    values = old.firm_id.map(agg.total)
    new = old.copy()
    new[VAR] = values
    dta[VAR] = values.to_numpy()
    labels[VAR] = f'{DESCRIPTION} USD t+1..t+3; none/incomplete disclosure = missing'
    annual_cols = []
    for horizon in (1, 2, 3):
        col = f'{PREFIX}_t{horizon}'
        annual_cols.append(col)
        w = window.loc[window.year.sub(window.VDyear).eq(horizon)]
        annual = w.groupby('firm_id').agg(rounds=('equity','size'),
            disclosed=('amount','count'),total=('amount',lambda x:x.sum(min_count=1)))
        annual.loc[annual.rounds.ne(annual.disclosed),'total'] = np.nan
        new[col] = old.firm_id.map(annual.total)
        dta[col] = new[col].to_numpy()
        labels[col] = f'{DESCRIPTION} USD in reference year +{horizon}; none/undisclosed = missing'
        print(stem, col, 'observed=',new[col].notna().sum(),
              'no_round=',(~old.firm_id.isin(annual.index)).sum(),
              'incomplete=',annual.total.isna().sum())
    # A no-round year is missing for its annual DV, but contributes no dollars
    # to the three-year sum. Compare only firms with a complete cumulative sum.
    valid = new[VAR].notna()
    assert np.allclose(new.loc[valid,annual_cols].sum(axis=1),new.loc[valid,VAR])
    # Pandas accepts value-label mappings by variable name; preserve all labels.
    cats = pd.read_stata(dta_path, convert_categoricals=True)
    maps = {}
    for col in cats:
        if isinstance(cats[col].dtype, pd.CategoricalDtype):
            pairs = pd.DataFrame({'code':dta[col], 'label':cats[col].astype(str)}).dropna().drop_duplicates()
            maps[col] = dict(zip(pairs.code.astype(int), pairs.label))
    for path in [csv_path,dta_path]:
        shutil.copy2(path,backup/path.name)
    new.to_csv(csv_path,index=False,encoding='utf-8-sig')
    dta.to_stata(dta_path,write_index=False,version=118,variable_labels=labels,value_labels=maps)
    check = pd.read_stata(dta_path,convert_categoricals=False)
    updated = [VAR] + annual_cols
    assert np.allclose(check[updated],new[updated],equal_nan=True)
    pd.testing.assert_frame_equal(new.drop(columns=updated),old.drop(columns=updated,errors='ignore'))
    print(stem, 'N=',len(new),'observed=',values.notna().sum(),'no_equity_round=',(~old.firm_id.isin(agg.index)).sum(),'incomplete_amount=',agg.total.isna().sum(),'sum_USD=',values.sum())
    window['target'] = stem
    audit_parts.append(window)
audit_name = 'followon_all_financing_win3_deal_audit.csv' if ALL_FINANCING else 'followon_equity_win3_deal_audit.csv'
pd.concat(audit_parts).to_csv(PKG/audit_name,index=False,encoding='utf-8-sig')
