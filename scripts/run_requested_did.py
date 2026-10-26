from pathlib import Path
root=Path('C:/Users/user/Documents/VD')
src=(root/'outputs/csdid_all_applications_corrected/MASTER_csdid_all_applications.do').read_text(encoding='utf-8-sig')
out=root/'outputs/refresh_did_20261023'
out.mkdir(exist_ok=True)
program=src[src.index('capture program drop construct_late'):src.index('frame change default')]
block=src[src.index('use "$P/firm_year_all_applications_and_truncation_specs.dta", clear',src.index('* PATENT QUALITY v4:')):]
block=block[:block.index('export delimited')]
for dv in ['grantedapp_norm','norm_cite_perpat_v4']:
    text='version 19\nclear all\nset more off\nset linesize 255\ncapture log close _all\n'
    text+=f'log using "{out.as_posix()}/{dv}.log", text replace\n'
    text+=program+'\nglobal P "'+(root/'outputs/csdid_all_applications_corrected').as_posix()+'"\n'
    text+=f'global Q "{out.as_posix()}"\n'
    text+=block.replace('local dv norm_cite_perpat_v4',f'local dv {dv}').replace('quality_v4_results.dta',dv+'_results.dta')
    text+='assert rc==0\ndisplay "REQUESTED_DID_COMPLETE"\nlog close\n'
    (out/(dv+'.do')).write_text(text,encoding='utf-8')
