clear all
set more off
global ROOT "C:/Users/user/Documents/VD/outputs/psm_final_2820_package"
global OUT "$ROOT/table3_original2820_full_results"
use "$ROOT/table3_original_2820_cross_section_v2.dta", clear
capture drop priorpatentdummy_VD
gen priorpatentdummy_VD = 1 - patentdummybyfiling
capture drop ln_grantedbyfiling_norm_win3
gen ln_grantedbyfiling_norm_win3 = log(grantedpatentbyfiling_norm_win3+1)

MethodInvocationException: 
Line |
   2 |  … -2:'); $b = $s.IndexOf('* End Table 3-2'); $s.Substring($a, $b-$a+15)
     |                                               ~~~~~~~~~~~~~~~~~~~~~~~~~~
     | Exception calling "Substring" with "2" argument(s): "startIndex ('-1') must be a non-negative value. (Parameter 'startIndex')
Actual value was -1."
display "TABLE3_2_TEST_COMPLETE"
exit, clear

