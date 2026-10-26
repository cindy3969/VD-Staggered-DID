"""Targeted, repeatable mechanical update of the existing requested v2 do-file."""
from pathlib import Path
import re
from rebuild_original2820_innovation import DO,OUT

def main():
    text=DO.read_text(encoding='utf-8-sig')
    if '* ORIGINAL2820_INNOVATION_REBUILT' in text:
        print('Already updated');return
    before=text
    text=text.replace('* See original2820_supplement_coverage.csv for measurement coverage.',
        '* Original-cohort innovation rebuilt from patent-level source data through 2024.\n'
        '* See innovation_original2820_rebuild_20261020/measurement_coverage.csv.\n'
        '* Original firm IDs, reference years and stored controls are unchanged.')
    text=text.replace('display as text "Supplemental coverage: not all firms have collected patent text/trajectory data."\ntabulate innovation_source_covered\ntabulate innovation_uncollected',
        '* ORIGINAL2820_INNOVATION_REBUILT\n'
        'display as text "Original 2820 firms. Innovation: complete reference+1..+3 windows through 2024."\n'
        'tabulate innov_window_complete, missing\n'
        'tabulate innovation_uncollected, missing\n'
        'tabulate fog_win3_status, missing\n'
        'tabulate novelty_status, missing\n'
        'tabulate selftotal_status, missing')
    # Repair deletion followed by self-reference; retain the user's explicit
    # 1-prior recoding in this do-file, without changing the stored controls.
    text=text.replace('gen priorpatentdummy_VD = 1 - priorpatentdummy_VD',
        '* This analysis retains your 1-prior coding: 1 means NO prior patent.\n'
        '* Stored DTA patentdummybyfiling and Priorpatent_VD are not changed.\n'
        'gen priorpatentdummy_VD = 1 - Priorpatent_VD')
    head,body=text.split('***Other innovation measures',1)
    body=body.replace('logit breakthrough_win3','fracreg logit breakthrough_win3')
    # Updated DTA already contains logs. Re-create safely for standalone section use.
    body=re.sub(r'(?m)^gen (ln_\w+) =',lambda m:'capture drop '+m[1]+'\ngen '+m[1]+' =',body)
    # Preserve original commands/specifications and add grouped output only.
    lines=body.splitlines(); result=[]; commands=[];group=[]; groupdv=None;exports=0;i=0
    while i<len(lines):
        line=lines[i]
        if re.match(r'^\s*outreg2\b',line):
            while line.rstrip().endswith('///') and i+1<len(lines):i+=1;line=lines[i]
            i+=1;continue
        match=re.match(r'^\s*(reghdfe|fracreg logit)\s+(\w+)\s',line)
        if not match:result.append(line);i+=1;continue
        command=[line]
        while command[-1].rstrip().endswith('///'):
            i+=1;command.append(lines[i])
        result.extend(command);commands.append('\n'.join(command));dv=match[2]
        if groupdv is not None:assert dv==groupdv,(dv,groupdv)
        groupdv=dv;name=f'INNO_{len(commands)}';group.append(name);result.append('estimates store '+name)
        if len(group)==4:
            mode='replace' if exports==0 else 'append'
            result.extend(['esttab '+' '.join(group)+' using "$OUT/Other_innovation_measures.rtf", '+mode+' ///',
                '    b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///',
                '    mtitles("(1)" "(2)" "(3)" "(4)") ///',
                '    stats(N r2, labels("Observations" "R-squared")) ///',
                '    title("DV: '+dv+'") ///',
                '    addnotes("Original 2820-firm cohort; original controls and fixed effects." ///',
                '    "Undefined or unobserved measurements remain missing; available N differs by DV." ///',
                '    "p-values in parentheses. Breakthrough share uses fractional logit.")'])
            group=[];groupdv=None;exports+=1
        i+=1
    assert not group and len(commands)>=32
    intro='''***Other innovation measures
* All variables below are reaggregated using ORIGINAL company and VDyear.
* Complete calendar window required; no-patent means/diversity are not zero.
* Status codes are labeled in the DTA. No blanket missing-to-zero replacement.
* breakthrough_win3 is a share, so fractional logit is used (not binary logit).
* cite_breadth_win3 is 0 for a patent with a verified empty reference list.
* New/old-domain counts require an observed, classified pre-reference portfolio.
tabstat nocite_win3 breakthrough_win3 desc_words_win3 fog_win3 ari_win3 ///
    neg_flesch_win3 figures_win3 sheets_win3 claims_win3 newpat_win3 oldpat_win3 ///
    newcpc_win3 cite_breadth_win3 self_citations_total_win3, ///
    statistics(N mean sd min max) columns(statistics)
'''
    updated=head+intro+'\n'.join(result)+'\n'
    assert len(re.findall(r'(?m)^\s*stcox\b',updated))==len(re.findall(r'(?m)^\s*stcox\b',before))
    DO.write_text(updated,encoding='utf-8')
    print('Updated existing v2:',len(commands),'innovation models;',exports,'four-column result tables')
    # Diagnostic runner contains only original model text with the data and
    # aliases required for this section, not a replacement user do-file.
    runner='''version 19
clear all
set more off
capture log close
log using "C:/Users/user/Documents/VD/outputs/innovation_original2820_rebuild_20261020/stata_innovation_test.log", text replace
use "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_original_2820_cross_section_v2.dta", clear
replace priorpatentdummy_VD = 1 - patentdummybyfiling
replace Earlystage_VD = earlystage
global OUT "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/table3_original2820_full_results"
capture mkdir "$OUT"
'''+intro+'\n'.join(result)+'\ndisplay "INNOVATION_TEST_FINISHED"\nlog close\n'
    (OUT/'test_existing_innovation_section.do').write_text(runner,encoding='utf-8')

if __name__=='__main__':main()
