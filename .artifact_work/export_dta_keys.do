clear all
set more off
use "C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms/260122 winsorization.dta", clear
keep firm_id OrganizationName VD VDyear Foundingyear
export delimited using "C:/Users/user/Documents/VD/.artifact_work/dta_keys.csv", replace quote
exit, clear
