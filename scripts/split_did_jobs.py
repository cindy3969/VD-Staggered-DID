from pathlib import Path
p=Path('C:/Users/user/Documents/VD/outputs/refresh_did_20261023')
for dv,groups in [('grantedapp_norm',['noprior','prior','nonlate','late','notyet']),('norm_cite_perpat_v4',['nonlate','late','notyet'])]:
 s=(p/(dv+'.do')).read_text()
 for group in groups:
  job=s.replace('foreach sample in all noprior prior nonlate late notyet {',f'foreach sample in {group} {{')
  job=job.replace(dv+'.log',dv+'_'+group+'.log').replace(dv+'_results.dta',dv+'_'+group+'_results.dta')
  (p/(dv+'_'+group+'.do')).write_text(job,encoding='utf-8')
