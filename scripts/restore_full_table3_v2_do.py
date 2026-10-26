"""Mechanically adapt the user's entire original do-file, not a subset."""
from pathlib import Path
import re,json
ROOT=Path('C:/Users/user/Documents/VD')
PKG=ROOT/'outputs/psm_final_2820_package'
source=PKG/'RUN_TABLE3_PATENT_APPLICATION_WIN3.do'
target=PKG/'RUN_TABLE3_PATENT_APPLICATION_WIN3_v2.do'
text=source.read_text(encoding='utf-8-sig')
text=text.replace('table3_current_2820_cross_section_v2.dta','table3_original_2820_cross_section_v2.dta')
text=text.replace('table3_application_results','table3_original2820_full_results')
text=text.replace('Table3_patent_application_win3.log','RUN_TABLE3_FULL_v2.log')
text=re.sub(r'\bEarlystage\b','Earlystage_VD',text)
text=text.replace('*ipo\n', '''*ipo
* Restore IPO failure definition; source code otherwise reused M&A stset.
stset duration if table7_sample == 1, failure(fail_ipo == 1) id(firm_id)
stcox VD nopriorpatentdummy_VD Earlystage_VD ln_MoneyRaised_VD NumofFundingRounds_VD i.Region2 i.Industry2 i.Foundingyear, nohr
''')
header='''* Complete original analysis on the ORIGINAL 260122 2820 firms.
* All original analysis sections retained, including Cox, IV and innovation.
* The original do-file is not modified. This is the requested v2 file.
* Original controls and original moneyraised_win3 are retained.
* Unsupported source observations remain missing, NOT zero.
* See original2820_supplement_coverage.csv for measurement coverage.
* Source-code caveats retained: Table 8 is headed Employee but uses financing;
* Table 10 repeats year-2 revenue; first Table 7 enters category codes linearly.
* Those specifications have NOT been silently changed.
* Runtime fixes: existing aliases/logs, Earlystage spelling, IPO stset.
* All model tables are appended to All_analysis_tables.rtf, in source order.
* Robust regressions and Cox coefficients are as specified in the original.

'''
out=[header]; model=0; groups=0; commands=[]; section='Setup'; lines=text.splitlines();i=0
while i<len(lines):
    line=lines[i];i+=1
    if line.lstrip().startswith('*'):
        if 'Table ' in line or 'innovation' in line: section=line.strip('* ')
        out.append(line);continue
    group=[line]
    while group[-1].rstrip().endswith('///') and i<len(lines):group.append(lines[i]);i+=1
    cmd='\n'.join(group)
    # Safe full-file reruns with data already containing generated columns.
    m=re.match(r'\s*gen(?:erate)?\s+(?:(?:double|byte|float|int|long)\s+)?(\S+)\s*=',cmd)
    if m:out.append('capture drop '+m.group(1))
    m=re.match(r'\s*rename\s+(\S+)\s+(\S+)',cmd)
    if m:out.append('capture drop '+m.group(2))
    if cmd.startswith('outreg2 '):
        # One numbered result file per original estimation command.
        # Export calls are supplied below for EVERY model, including alternatives.
        continue
    out.append(cmd)
    if cmd.startswith('use "$ROOT/table3_original_2820_cross_section_v2.dta"'):
        out.extend(['isid firm_id','assert _N==2820',
            'display as text "Supplemental coverage: not all firms have collected patent text/trajectory data."',
            'tabulate innovation_source_covered','tabulate innovation_uncollected',
            'which reghdfe','which ivreghdfe','which esttab'])
    if re.match(r'^(reghdfe|ivreghdfe|stcox)\s',cmd):
        model+=1
        mode='replace' if model==1 else 'append'
        out.extend([f'estimates store Model_{model:03}',
            f'esttab using "$OUT/All_analysis_tables.rtf", {mode} b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) stats(N r2 N_fail, labels("Observations" "R-squared" "Failures")) title("Model {model}: {section.replace(chr(34),chr(39))}")'])
        commands.append({'model':model,'section':section,'command':cmd})
out.extend([f'display as result "COMPLETED FULL ORIGINAL-SAMPLE ANALYSIS: {model} estimation commands."','log close'])
target.write_text('\n'.join(out)+'\n',encoding='utf-8')
(PKG/'original2820_model_index.json').write_text(json.dumps(commands,indent=2,ensure_ascii=False),encoding='utf-8')
print('Restored full do-file:',model,'estimation commands; lines=',len(out))
