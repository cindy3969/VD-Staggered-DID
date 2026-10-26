version 19
clear all
set more off
global OLD "C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms"
global OUT "C:/Users/user/Documents/VD/outputs/psm_final_2820_package"
capture log close
log using "$OUT/SCAN_ALL_DTA_FOR_PSM.log", text replace

local files : dir "$OLD" files "*.dta"
foreach f of local files {
    quietly use "$OLD/`f'", clear
    local hit=0
    foreach v in _pscore _weight _id _n1 _nn _pdif pscore pscore2 {
        capture confirm variable `v'
        if !_rc local hit=1
    }
    if `hit' {
        display as text _newline "FILE: `f' | N=" _N
        foreach v in _pscore _weight _id _n1 _nn _pdif pscore pscore2 {
            capture confirm variable `v'
            if !_rc {
                quietly count if !missing(`v')
                local nonmiss=r(N)
                quietly summarize `v', meanonly
                display as result "  `v': nonmissing=" `nonmiss' ///
                    " min=" r(min) " max=" r(max)
            }
        }
        capture confirm variable VD_Backing
        if !_rc {
            quietly count if VD_Backing==1
            display as result "  VD_Backing=1: " r(N)
            capture confirm variable _weight
            if !_rc {
                quietly count if VD_Backing==1 & _weight==1
                display as result "  treated with weight 1: " r(N)
                quietly count if VD_Backing==0 & _weight==1
                display as result "  controls with weight 1: " r(N)
            }
        }
        capture confirm variable VD
        if !_rc {
            quietly count if VD==1
            display as result "  VD=1: " r(N)
        }
    }
}
log close
exit, clear
