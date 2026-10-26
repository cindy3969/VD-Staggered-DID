from pathlib import Path
from collections import defaultdict
import shutil
import sys
import pandas as pd
import openpyxl

PKG = Path(__file__).resolve().parent
SOURCE = Path('C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms/2010 2015 Crunchbase deals merged_v4.xlsx')
STEM = 'table3_current_2820_cross_section'

def inspect():
    current = pd.read_csv(PKG / (STEM + '.csv'))
    targets = current.loc[current.Industry2_label.astype(str).eq('0')]
    ids = set(targets.firm_id.astype(int))
    names = set(targets.OrganizationName.str.strip().str.casefold())
    byid, byname = defaultdict(list), defaultdict(list)
    book = openpyxl.load_workbook(SOURCE, read_only=True, data_only=True)
    for row in book.active.iter_rows(min_row=3, values_only=True):
        name = str(row[3]).strip().casefold()
        if row[0] in ids or name in names:
            record = (row[0], row[3], row[86])
            byid[row[0]].append(record)
            byname[name].append(record)
    book.close()
    bio = {'Biotechnology', 'Health Care', 'Healthcare'}
    software = {'Commerce and Shopping', 'Apps', 'Artificial Intelligence (AI)', 'Artificial Intelligence', 'Data and Analytics', 'Financial Services', 'Information Technology', 'Internet Services', 'Blockchain and Cryptocurrency', 'Gaming', 'Software', 'Mobile', 'Privacy and Security', 'Navigation and Mapping'}
    hardware = {'Consumer Electronics', 'Hardware', 'Energy', 'Manufacturing', 'Transportation', 'Science and Engineering', 'Natural Resources', 'Sustainability', 'Robotics'}
    result = []
    inferred = {
        12005: ('Description: protein/materials technology', 'Hardware/Manufacturing/DeepTech'),
        54042: ('Description: autonomous service robot manufacturer', 'Hardware/Manufacturing/DeepTech'),
        44378: ('Description: workforce engagement platform', 'Software/IT services'),
        44487: ('Industries: Boating, Outdoors, Recreation', 'Other'),
        33413: ('Description: enterprise data acquisition and integration software', 'Software/IT services'),
        48594: ('Description: deep-learning cybersecurity software', 'Software/IT services'),
        33153: ('Industries: Analytics, Big Data, Enterprise Software, Information Technology, Software', 'Software/IT services'),
    }
    for t in targets.itertuples():
        name = t.OrganizationName.strip().casefold()
        records = byid.get(t.firm_id, [])
        if records:
            assert all(str(r[1]).strip().casefold() == name for r in records), (t.OrganizationName, records)
            method = 'firm_id and name verified'
        else:
            records = byname.get(name, [])
            method = 'exact name'
        assert records, t.OrganizationName
        classes = {str(r[2]).strip() for r in records}
        assert len(classes) == 1, (t.OrganizationName, classes)
        cl = classes.pop()
        label = ('0' if cl in {'0', 'None', '', 'False'} else
                 'Bio/Healthcare' if cl in bio else
                 'Software/IT services' if cl in software else
                 'Hardware/Manufacturing/DeepTech' if cl in hardware else 'Other')
        if label == '0' and t.firm_id in inferred:
            cl, label = inferred[t.firm_id]
            method += '; inferred from source description/Industries'
        result.append(dict(firm_id=t.firm_id, OrganizationName=t.OrganizationName,
                           source_classification=cl, Industry2_label=label, match_method=method))
    return pd.DataFrame(result)

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    fixes = inspect()
    print(fixes.to_string(index=False))
    if '--apply' in sys.argv:
        backup = PKG / 'backups' / 'before_industry2_source_repair_20261014'
        backup.mkdir(parents=True, exist_ok=True)
        for suffix in ['.csv', '.dta']:
            dest = backup / (STEM + suffix)
            if not dest.exists(): shutil.copy2(PKG / (STEM + suffix), dest)
        fixes.to_csv(PKG / 'industry2_source_corrections.csv', index=False, encoding='utf-8-sig')
