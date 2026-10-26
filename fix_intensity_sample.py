from pathlib import Path
import shutil
p=Path('outputs/vd_intensity/replicate_tables_3_1_to_3_7.do')
backup=p.with_name('replicate_tables_before_removing_both_periods_filter.do')
if not backup.exists():shutil.copy2(p,backup)
s=p.read_text(encoding='utf-8-sig')
s=s.replace('* Same complete-case sample across four columns WITHIN each table.','* Same complete-case sample across four columns WITHIN each table.\n* Do not restrict firms to observed pre AND post years; audit that coverage only.')
s=s.replace('* Keep firms observed both before and after treatment in the usable sample.','* Audit pre/post coverage without excluding post-only firms.')
s=s.replace('    keep if minpost==0 & maxpost==1\n','')
s=s.replace('    quietly count if tag2\n','    quietly count if tag2 & minpost==0 & maxpost==1\n')
s=s.replace("    assert `both'>1","    assert `complete_n'>1")
p.write_text(s,encoding='utf8')
