clear all
set more off
capture log close
log using "C:/Users/user/Documents/VD/.artifact_work/inspect_details.log", replace text
use "C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms/260122 winsorization.dta", clear
describe
count
capture count if weight==1
capture noisily codebook firm_id OrganizationName OrganizationNameURL VD VDyear VDyear2 Foundingyear Founding_Year SeriesB earlystage weight
capture noisily list firm_id OrganizationName OrganizationNameURL VD VDyear VDyear2 Foundingyear Founding_Year SeriesB earlystage weight in 1/10, clean noobs
log close
exit, clear
