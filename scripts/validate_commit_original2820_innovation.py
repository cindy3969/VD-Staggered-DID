"""Validate Stata candidate against original data before in-place replacement."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess
import numpy as np
import pandas as pd
from rebuild_original2820_innovation import ROOT,OUT,PKG,PROD

def main():
    before=pd.read_stata(PROD,convert_categoricals=False).sort_values('firm_id').reset_index(drop=True)
    update=pd.read_stata(OUT/'innovation_update.dta',convert_categoricals=False).sort_values('firm_id').reset_index(drop=True)
    subprocess.run(['C:/Program Files/StataNow19/StataSE-64.exe','/e','do',str(OUT/'merge_validated_innovation.do')],
                   creationflags=subprocess.CREATE_NO_WINDOW,timeout=180,check=True)
    log=(OUT/'merge_validation.log').read_text(encoding='utf-8',errors='replace')
    assert not re.search(r'^r\(\d+\);',log,re.M),log[-3000:]
    candidate=OUT/'validated_candidate.dta'
    after=pd.read_stata(candidate,convert_categoricals=False).sort_values('firm_id').reset_index(drop=True)
    assert len(after)==2820 and after.firm_id.is_unique and after.VD.value_counts().to_dict()=={0:1410,1:1410}
    unchanged=[c for c in before if c not in update or c=='firm_id']
    pd.testing.assert_frame_equal(before[unchanged],after[unchanged],check_dtype=False,check_exact=True)
    pd.testing.assert_frame_equal(after[update.columns],update,check_dtype=False,check_exact=True)
    legacy_path=Path('C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms/260122 winsorization.dta')
    legacy=pd.read_stata(legacy_path,convert_categoricals=False).sort_values('firm_id').reset_index(drop=True)
    pd.testing.assert_frame_equal(legacy,after[legacy.columns],check_dtype=False,check_exact=True)
    with pd.io.stata.StataReader(PROD) as reader:old_labels=reader.variable_labels()
    with pd.io.stata.StataReader(candidate) as reader:new_labels=reader.variable_labels()
    assert all(old_labels[c]==new_labels[c] for c in unchanged)
    changes=[]
    for c in update:
        if c=='firm_id':continue
        if c in before:
            equal=np.isclose(before[c],after[c],equal_nan=True)
            changes.append({'variable':c,'changed_firms':int((~equal).sum()),
                'before_nonmissing':int(before[c].notna().sum()),'after_nonmissing':int(after[c].notna().sum()),
                'after_zero':int(after[c].eq(0).sum())})
        else:changes.append({'variable':c,'changed_firms':len(after),'before_nonmissing':0,
                           'after_nonmissing':int(after[c].notna().sum()),'after_zero':int(after[c].eq(0).sum())})
    pd.DataFrame(changes).to_csv(OUT/'before_after_measurements.csv',index=False)
    qa=json.loads((OUT/'validation.json').read_text())
    qa['production_merge']={'matched_firms':2820,'original_legacy_columns_preserved':len(legacy.columns),
        'other_existing_columns_preserved':len(unchanged),'all_noninnovation_values_unchanged':True,
        'original_variable_labels_preserved':True,'updated_columns':len(update.columns)-1,
        'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest()}
    # Only now replace the requested existing file. Backup already exists.
    shutil.copy2(candidate,PROD)
    qa['production_merge']['saved_path']=str(PROD)
    (OUT/'validation.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
    print(json.dumps(qa['production_merge'],indent=2))

if __name__=='__main__':main()
