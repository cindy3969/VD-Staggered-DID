"""Instrument an execution copy, preserving the user's two source do-files."""
from pathlib import Path
import json, re, hashlib, shutil
ROOT=Path(__file__).resolve().parents[1]
PKG=ROOT/'outputs/psm_final_2820_package'
OUT=ROOT/'outputs/table_update_20261019'
OUT.mkdir(exist_ok=True)
source=PKG/'RUN_TABLE3_PATENT_APPLICATION_WIN3.do'
text=source.read_text(encoding='utf-8-sig')
for f in [source,PKG/'RUN_INNOVATION_WIN3.do']:
    target=OUT/(f.stem+'_source_snapshot.do')
    if not target.exists(): shutil.copy2(f,target)
helper=r'''
postfile capture_results int model str100 term double b se p N r2 F df fail cdf kp using "__OUT__/main_coefficients.dta", replace
capture program drop capture_model
program define capture_model
    syntax, ID(integer)
    tempname B V bb ss pp
    matrix `B'=e(b)
    matrix `V'=e(V)
    local names : colfullnames `B'
    local k=colsof(`B')
    forvalues j=1/`k' {
        local term : word `j' of `names'
        scalar `bb'=`B'[1,`j']
        scalar `ss'=sqrt(`V'[`j',`j'])
        scalar `pp'=.
        if `ss'>0 & !missing(`ss') {
            if !missing(e(df_r)) scalar `pp'=2*ttail(e(df_r),abs(`bb'/`ss'))
            else scalar `pp'=2*normal(-abs(`bb'/`ss'))
        }
        post capture_results (`id') ("`term'") (`bb') (`ss') (`pp') (e(N)) (e(r2)) (e(F)) (e(df_r)) (e(N_fail)) (e(cdf)) (e(widstat))
    }
    estimates save "__OUT__/main_model_`id'.ster", replace
end
'''.replace('__OUT__',OUT.as_posix())
lines=text.splitlines(); output=[]; commands=[]; i=0; section='setup'; skip=False; model=0
while i<len(lines):
    line=lines[i]; start=i+1; i+=1
    if line.startswith('* Table 8: Employee'): skip=True
    if line.startswith('*******************APPENDIX'): skip=False
    if skip: continue
    if line.startswith('* Table 3: Patent quantity'):
        output.append(r'''
* Recompute Tables 1 and 2 from the exact Table 1 variable list.
local tablevars patent_application_win3 VD nopriorpatentdummy_VD Earlystage_VD MoneyRaised_VD NumofFundingRounds_VD ind_1 ind_2 ind_4 reg_1 reg_2 reg_3
tempname summ corr
postfile `summ' str40 variable double N mean sd min max using "$OUT/table1_stats.dta", replace
foreach v of local tablevars {
    quietly summarize `v'
    post `summ' ("`v'") (r(N)) (r(mean)) (r(sd)) (r(min)) (r(max))
}
postclose `summ'
postfile `corr' str40 variable1 str40 variable2 double N r p using "$OUT/table2_correlations.dta", replace
foreach v of local tablevars {
    foreach w of local tablevars {
        quietly correlate `v' `w'
        local n=r(N)
        local rho=r(rho)
        local prob=.
        if abs(`rho')<1 local prob=2*ttail(`n'-2,abs(`rho')*sqrt((`n'-2)/(1-`rho'^2)))
        post `corr' ("`v'") ("`w'") (`n') (`rho') (`prob')
    }
}
postclose `corr'
''')
    if line.lstrip().startswith('*'):
        if re.search(r'[Tt]able',line): section=line.strip('* ').strip()
        output.append(line); continue
    group=[line]
    while group[-1].rstrip().endswith('///') and i<len(lines): group.append(lines[i]); i+=1
    command='\n'.join(group)
    # Fix a renamed variable referenced by its old spelling in a sample check.
    command=re.sub(r'\bEarlystage\b','Earlystage_VD',command)
    # The exploratory IPO subsection omitted stset and otherwise reused M&A.
    if command.strip()=='capture drop ipo_sample' and start<400:
        output.append('stset duration if table7_sample == 1, failure(fail_ipo == 1) id(firm_id)')
    # Isolate logs and presentation exports; estimation commands unchanged.
    if command.startswith('global OUT '): command='global OUT "'+OUT.as_posix()+'"'
    if command.startswith('outreg2 '): command='capture noisily '+command
    output.append(command)
    if command.startswith('use "$ROOT/table3_current_2820_cross_section_v2.dta"'): output.append(helper)
    if re.match(r'^(reghdfe|ivreghdfe|stcox)\s',command):
        model+=1
        commands.append(dict(model=model,line=start,section=section,command=command))
        output.append(f'capture_model, id({model})')
output.extend(['postclose capture_results','preserve',
    f'use "{OUT.as_posix()}/main_coefficients.dta", clear',
    f'export delimited using "{OUT.as_posix()}/main_coefficients.csv", replace','restore',
    'log close',f'do "{PKG.as_posix()}/RUN_INNOVATION_WIN3.do"'])
(OUT/'RUN_TABLE_UPDATE.do').write_text('\n'.join(output)+'\n',encoding='utf-8')
(OUT/'model_commands.json').write_text(json.dumps(commands,indent=2,ensure_ascii=True),encoding='utf-8')
print('Instrumented models',model)
print('Source SHA256',hashlib.sha256(source.read_bytes()).hexdigest())
