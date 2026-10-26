version 19
clear all
set more off
global OLD "C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms"
global OUT "C:/Users/user/Documents/VD/outputs/psm_final_2820_package"
capture log close
log using "$OUT/AUDIT_ARCHIVED_PSM_FILES.log", text replace

foreach f in "all_with_pscore.dta" "all_with_pscore 2.dta" "matchedset.dta" "240626.dta" "240626 2.dta" {
    display as text _newline "============================================================"
    display as result "FILE: `f'"
    use "$OLD/`f'", clear
    display as result "N = " _N
    capture noisily describe VD_Backing VD _pscore _weight _id _n1 _nn _pdif ///
        pscore pscore2 Founding_Year VD_Year Industry2 Region2 ///
        NumberOfFunding_Rounds_FirstVD NumberOfFunding_Rounds_FirstVC ///
        ln_Total_Funding_Amount_FirstVD ln_Total_Funding_Amount_FirstVC ///
        Patents_VD PatentGranted_VD Grant_VD TimeToFirst_VC TimeToFirst_VD
    capture noisily summarize _pscore _weight _id _n1 _nn _pdif, detail
    capture noisily tab VD_Backing
    capture noisily tab VD
    capture noisily tab VD_Backing _weight, missing
    capture noisily tab VD _weight, missing
    capture noisily codebook Industry2 Region2
}

log close
exit, clear
