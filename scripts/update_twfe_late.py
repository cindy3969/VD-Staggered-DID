from pathlib import Path
p=Path('C:/Users/user/Documents/VD/outputs/vd_intensity/replicate_tables_3_1_to_3_7.do')
s=p.read_text(encoding='utf-8-sig')
b=p.with_suffix('.before_late_20261023.bak')
if not b.exists(): b.write_bytes(p.read_bytes())
s=s.replace('early','late').replace('Early','Late')
s=s.replace('generate byte late=late_stage_G', '''* Series classification from audited equity-round histories; original year-end timing retained.
preserve
use "`root'/outputs/csdid_all_applications_corrected/firm_year_all_applications_and_truncation_specs.dta", clear
keep organization_name year stage_endyear_text stage_preyear_text
isid organization_name year
tempfile stages
save `stages'
restore
merge 1:1 organization_name year using `stages', keep(master match) nogen
gen byte late_year=.
replace late_year=1 if regexm(lower(strtrim(stage_endyear_text)),"^series [c-z][0-9]*$")
replace late_year=0 if regexm(lower(strtrim(stage_endyear_text)),"^series [ab][0-9]*$") | inlist(lower(strtrim(stage_endyear_text)),"seed","pre-seed","angel")
gen byte late_at_G=late_year if year==first_vd_year
bysort full_firm_id: egen byte late=max(late_at_G)
drop late_at_G
xtset full_firm_id year''')
s=s.replace('generate double lag_late=L.late_stage','''generate byte lag_late=.
replace lag_late=1 if regexm(lower(strtrim(stage_preyear_text)),"^series [c-z][0-9]*$")
replace lag_late=0 if regexm(lower(strtrim(stage_preyear_text)),"^series [ab][0-9]*$") | inlist(lower(strtrim(stage_preyear_text)),"seed","pre-seed","angel")''')
s=s.replace('    preserve\n    egen byte tag0', '    if !inlist(`table\',1,4) continue\n    preserve\n    egen byte tag0')
s=s.replace('forvalues t=1/8 {','foreach t in 1 4 {')
s=s.replace('* Created 2026-10-19.', '* Current Table 13 = legacy 3-1; Table 14 = legacy 3-4. Only these two run.\n* Late = explicit Series C+; Seed/Angel/A/B = 0; unknown = missing.\n* Created 2026-10-19.')
s=s.replace('vd_lat er','vd_earlier').replace('vd_latelier_debt_rounds','vd_earlier_debt_rounds')
# Avoid accidental replacement in unrelated variable vd_earlier_debt_rounds.
s=s.replace('vd_lateier_debt_rounds','vd_earlier_debt_rounds')
p.write_text(s,encoding='utf-8')
