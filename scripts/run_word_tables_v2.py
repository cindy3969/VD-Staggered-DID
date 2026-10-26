from pathlib import Path
import re,json,shutil
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/table_run_v2_20261020'
OUT.mkdir(exist_ok=True)
SRC=ROOT/'outputs/psm_final_2820_package/RUN_TABLE3_PATENT_APPLICATION_WIN3_v2.do'
shutil.copy2(SRC,OUT/'source_snapshot.do')
helper=r'''
postfile capture_results int model str120 term double b se p N r2 F df fail kp using "$OUT/coefficients.dta", replace
program define capture_model
 syntax, ID(integer)
 tempname B V bb ss pp
 matrix `B'=e(b)
 matrix `V'=e(V)
 local names : colfullnames `B'
 forvalues j=1/`=colsof(`B')' {
  local term : word `j' of `names'
  scalar `bb'=`B'[1,`j']
  scalar `ss'=sqrt(`V'[`j',`j'])
  scalar `pp'=.
  if `ss'>0 & !missing(`ss') {
   if !missing(e(df_r)) & e(cmd)!="ppmlhdfe" scalar `pp'=2*ttail(e(df_r),abs(`bb'/`ss'))
   else scalar `pp'=2*normal(-abs(`bb'/`ss'))
  }
  post capture_results (`id') ("`term'") (`bb') (`ss') (`pp') (e(N)) (e(r2)) (e(F)) (e(df_r)) (e(N_fail)) (e(widstat))
 }
end
'''
stats=r'''
local tablevars patent_application_win3 VD priorpatentdummy_VD Earlystage_VD MoneyRaised_VD NumofFundingRounds_VD ind_1 ind_2 ind_4 reg_1 reg_2 reg_3
tempname sm cr
postfile `sm' str40 variable double N mean sd min max using "$OUT/summary.dta", replace
foreach v of local tablevars {
 quietly summarize `v'
 post `sm' ("`v'") (r(N)) (r(mean)) (r(sd)) (r(min)) (r(max))
}
postclose `sm'
postfile `cr' str40 variable1 str40 variable2 double N r p using "$OUT/correlations.dta", replace
foreach v of local tablevars {
 foreach w of local tablevars {
  quietly correlate `v' `w'
  local n=r(N)
  local rho=r(rho)
  local p=.
  if abs(`rho')<1 local p=2*ttail(`n'-2,abs(`rho')*sqrt((`n'-2)/(1-`rho'^2)))
  post `cr' ("`v'") ("`w'") (`n') (`rho') (`p')
 }
}
postclose `cr'
'''
lines=SRC.read_text(encoding='utf-8-sig').splitlines()
out=[]; meta=[]; i=0; skip=False; section=''; mid=0
while i<len(lines):
 line=lines[i]; start=i+1;i+=1
 group=[line]
 while group[-1].rstrip().endswith('///') and i<len(lines):
  group.append(lines[i]);i+=1
 cmd='\n'.join(group); stripped=cmd.lstrip()
 if stripped.startswith('* Table 8:'):skip=True
 if '*******************APPENDIX' in cmd:skip=False
 if skip:continue
 if stripped.startswith('*'):
  if re.search(r'[Tt]able|Other innovation',line):section=line.strip('* ')
  # Remove whole commented continuation commands, not just their first line.
  out.append(cmd);continue
 if not stripped:out.append(cmd);continue
 if re.match(r'(outreg2|esttab)\b',stripped):continue
 if stripped.startswith('global OUT '):cmd=f'global OUT "{OUT.as_posix()}"'
 if stripped.startswith('tatstast '):cmd=cmd.replace('tatstast','tabstat',1)
 cmd=re.sub(r'\bEarlystage\b','Earlystage_VD',cmd)
 cmd=re.sub(r'\bgunning_fog_win3\b','fog_win3',cmd)
 if stripped=='capture drop ipo_sample' and start<470:
  out.append('stset duration if table7_sample == 1, failure(fail_ipo == 1) id(firm_id)')
 if stripped.startswith('save "$OUT/table3_2_analysis'):continue
 out.append(cmd)
 if stripped.startswith('use "$ROOT/'):out.append(helper)
 if stripped.startswith('pwcorr '):out.append(stats)
 if re.match(r'^(reghdfe|ivreghdfe|stcox|fracreg|ppmlhdfe|margins)\s',stripped):
  mid+=1;meta.append(dict(model=mid,line=start,section=section,command=cmd))
  out.append(f'capture_model, id({mid})')
out+=['postclose capture_results','display "WORD_TABLES_RUN_COMPLETE"','log close']
(OUT/'execute_no_excel.do').write_text('\n'.join(out)+'\n',encoding='utf-8')
(OUT/'models.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
print(f'{mid} estimates; no Excel export commands.')
