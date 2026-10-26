from pathlib import Path
import pandas as pd
import html
R=Path(r'C:\Users\user\Documents\VD\outputs\csdid_all_applications_corrected\citation_quality_20261019')
parts=['''<!DOCTYPE html><meta charset="utf-8"><title>Tables 11–12: annual patent quality</title><style>body{max-width:1200px;margin:35px auto;font:16px Georgia,serif;color:#171717}table{border-collapse:collapse;width:100%;margin:18px 0}th,td{padding:8px 12px;text-align:center}th:first-child,td:first-child{text-align:left}thead{border-top:2px solid;border-bottom:1px solid}tbody{border-bottom:2px solid}h1{font-size:24px}h2{font-size:20px}.note{font:14px Arial,sans-serif;line-height:1.55}.p{font-size:14px}.warn{background:#fff2d5;padding:15px}@media print{section{break-after:page}}</style><h1>Tables 11–12. VD and annual patent quality</h1><p class="note">DV: normalized citations per ultimately granted application filed in firm-year y. No log transformation and no three-year window. Citation observation cutoff: 2024. No granted applications in year y: missing outcome, following the original v1–v4 convention.</p>''']
labels={1:'Filing-year × citation-year normalization',2:'Filing-year × citation-year × CPC3 normalization',3:'Exposure-adjusted rate, filing-cohort normalized',4:'Cumulative citations, filing-year × CPC3 normalized'}
allresults=[]
for v in range(1,5):
    d=pd.read_csv(R/f'quality_v{v}_results.csv'); d['version']=v; allresults.append(d)
    def row(sample,aggregation,effect=None):
        z=d[d['sample'].eq(sample)&d.aggregation.eq(aggregation)]
        if effect is not None: z=z[z.effect.eq(effect)]
        return None if len(z)==0 else z.iloc[0]
    def fmt(r,se=False):
        if r is None or r.rc!=0 or pd.isna(r.att) or pd.isna(r.se) or r.se<=0: return 'Not estimable'
        star='***' if r.p<.01 else '**' if r.p<.05 else '*' if r.p<.1 else ''
        return f'{r.att:.3f}{star} ({r.se if se else r.p:.3f})'
    samples=['all','noprior','prior','early','late']
    t11=[]
    for title,agg,effect in [('Simple ATT','simple',None),('Aggregated event study ATT','event','Post_avg')]:
        t11.append([title]+[fmt(row(s,agg,effect)) for s in samples])
    t11 += [[title]+['Yes']*5 for title in ['Controls','Region FE','Industry FE']]
    t11 += [[title]+[int(d[d['sample'].eq(s)].iloc[0][col]) for s in samples] for title,col in [('Observations','N'),('Firms','firms')]]
    t11 += [['Control']+['Never-treated']*5]
    t11=pd.DataFrame(t11,columns=['Effect','All firms','No prior patent','Prior patent','Early stage','Late stage'])
    t11.to_csv(R/f'Table11_v{v}.csv',index=False)
    t12=[]
    t12.append(['Simple-aggregated effect']+[fmt(row(s,'simple'),True) for s in ['all','notyet']])
    for t in range(-4,5):
        term=f'Tm{abs(t)}' if t<0 else f'Tp{t}'
        t12.append([f'Event time {t}']+[fmt(row(s,'event',term),True) for s in ['all','notyet']])
    t12.append(['Dynamic-aggregated effect']+[fmt(row(s,'event','Post_avg'),True) for s in ['all','notyet']])
    t12.append(['Group-aggregated effect']+[fmt(row(s,'group','GAverage'),True) for s in ['all','notyet']])
    t12=pd.DataFrame(t12,columns=['Effect','Never-treated','Not-yet-treated'])
    t12.to_csv(R/f'Table12_v{v}.csv',index=False)
    parts.append(f'<section><h2>Table 11 — v{v}: {labels[v]}</h2>'+t11.to_html(index=False,border=0)+'<p class="note">p-values in parentheses. * p&lt;0.10, ** p&lt;0.05, *** p&lt;0.01. Event aggregate: Post_avg from window(−4,4). Counts describe complete-case input, as in the existing master; individual ATT(g,t) pairs can use fewer observations.</p></section>')
    parts.append(f'<section><h2>Table 12 — v{v}: {labels[v]}</h2>'+t12.to_html(index=False,border=0)+'<p class="note">Standard errors in parentheses. Same DRIPW controls and subgroup definitions as the existing master. Not estimable means a failed or unavailable estimate; it is not a zero effect.</p></section>')
allresults=pd.concat(allresults,ignore_index=True)
allresults.to_csv(R/'all_quality_DiD_results.csv',index=False)
parts.append('''<div class="note warn">Interpretation: these DVs condition on having ultimately granted applications in the filing year. The treatment may itself affect that selection. All patent qualities use citations observed through 2024, including citations received after the filing year; they measure ex-post quality of that filing cohort, not citation receipts in that calendar year. Normalization does not eliminate unobserved future grant/citation selection. Original earlier DiD citation-date results are superseded for these outcomes.</div>''')
(R/'Tables11_12_annual_quality.html').write_text('\n'.join(parts),encoding='utf-8')
print(allresults[(allresults['sample']=='all')&(allresults.aggregation=='simple')].to_string(index=False))
print('Failed rows:',int(allresults.rc.ne(0).sum()))
