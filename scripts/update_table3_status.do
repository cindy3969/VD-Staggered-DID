version 19
clear all
set more off

local pkg "C:/Users/user/Documents/VD/outputs/psm_final_2820_package"
local target "`pkg'/table3_current_2820_cross_section_v2.dta"
local lookup "`pkg'/_crunchbase_status_lookup.dta"
local backup "`pkg'/backups/before_status_update_20261015/table3_current_2820_cross_section_v2.dta"

capture mkdir "`pkg'/backups/before_status_update_20261015"
copy "`target'" "`backup'", replace

use "`target'", clear
isid firm_id
capture confirm variable status
if !_rc drop status
capture confirm variable m_a
if !_rc drop m_a
capture confirm variable ipo
if !_rc drop ipo
capture confirm variable defunct
if !_rc drop defunct
capture confirm variable status_year
if !_rc drop status_year
capture confirm variable status_date
if !_rc drop status_date

merge 1:1 firm_id using "`lookup'", assert(match) nogen
assert inlist(status, "acquired", "merged", "public", "defunct", "private")
assert inlist(m_a, 0, 1) & inlist(ipo, 0, 1) & inlist(defunct, 0, 1)
assert m_a == inlist(status, "acquired", "merged")
assert ipo == (status == "public")
assert defunct == (status == "defunct")
assert m_a + ipo + defunct <= 1

label variable status "Post-VD/current firm status from Crunchbase"
label variable m_a "M&A outcome (acquired or merged)"
label variable ipo "IPO/public outcome"
label variable defunct "Defunct/closed outcome"
label variable status_year "Post-VD exit/event year from Crunchbase"
label variable status_date "Exact Crunchbase event date (YYYY-MM-DD), when available"
compress
save "`target'", replace

tabulate status, missing
summarize m_a ipo defunct
describe status m_a ipo defunct status_year status_date
