from pathlib import Path
import json, html
import pandas as pd
R=Path(r'C:\Users\user\Documents\VD\outputs\table4_window3_39249_20261019')
d=pd.read_csv(R/'coefficients.csv')
q=json.loads((R/'QA.json').read_text())
terms={'VD':'VD','VD_prior':'VD × Prior Patent VD','VD_early':'VD × Early Stage VD','priorpatentdummy_VD':'Prior Patent VD','earlystage':'Early Stage VD','ln_MoneyRaised_VD':'Log(Total Funding Amount VD)','NumofFundingRounds_VD':'Number of Funding Rounds VD','_cons':'Constant'}
parts=['''<!DOCTYPE html><html><meta charset="utf-8"><title>Table 4 — Post-VD Patent Quality</title><style>body{font:16px Georgia,serif;max-width:1050px;margin:40px auto;color:#171717}table{border-collapse:collapse;width:100%;margin:18px 0}th,td{padding:8px 12px;text-align:center}th:first-child,td:first-child{text-align:left;width:44%}thead{border-top:2px solid;border-bottom:1px solid}tbody{border-bottom:2px solid}h2{font-size:20px;margin-top:45px}.p{font-size:14px;color:#444}.note{font:14px Arial,sans-serif;line-height:1.6}.warning{background:#fff2d5;padding:14px} @media print{section{break-after:page}body{margin:0}}</style><h1>Table 4. VD Backing and Post-VD Patent Quality</h1>''']
parts.append('<p class="note warning">Date correction: annual citations use the citing patent’s grant date. Earlier results used the cited patent’s grant-month field and should not be interpreted as annual forward-citation effects.</p>')
for sample in ['complete','full']:
    for method,label in [('cohort','Filing year × citation year'),('cpc','Filing year × citation year × primary CPC3')]:
        x=d[(d['sample']==sample)&(d.method==method)]
        parts.append(f'<section><h2>{label} normalization — {"Complete 3-year windows" if sample=="complete" else "Full matched sample (includes incomplete windows)"}</h2><p><i>DV: ln(1 + normalized citations per granted application), filing window t+1 to t+3</i></p><table><thead><tr><th></th>'+''.join(f'<th>({j})</th>' for j in range(1,5))+'</tr></thead><tbody>')
        for term,title in terms.items():
            parts.append('<tr><td><i>'+title+'</i></td>')
            for j in range(1,5):
                r=x[(x.model==j)&(x.term==term)]
                if len(r):
                    r=r.iloc[0]; star='***' if r.p<.01 else '**' if r.p<.05 else '*' if r.p<.1 else ''
                    parts.append(f'<td>{r.b:.3f}{star}<br><span class="p">({r.p:.3f})</span></td>')
                else: parts.append('<td></td>')
            parts.append('</tr>')
        for label,col in [('Region FE',None),('Industry FE',None),('Founding-year FE',None),('Observations','N'),('R-squared','r2')]:
            parts.append('<tr><td>'+label+'</td>')
            for j in range(1,5):
                r=x[x.model.eq(j)].iloc[0]
                v='Yes' if col is None else f'{r[col]:,.0f}' if col=='N' else f'{r[col]:.3f}'
                parts.append('<td>'+v+'</td>')
            parts.append('</tr>')
        parts.append('</tbody></table><p class="note">Heteroskedasticity-robust p-values in parentheses. * p&lt;0.10, ** p&lt;0.05, *** p&lt;0.01. Controls are measured at the existing VD/pseudo-treatment reference year. Year FE means founding-year FE, following the current analysis specification. Full matched universe: 2,820 firms.</p></section>')
parts.append('''<h2>Construction and interpretation</h2><div class="note"><p>The input universe contains 39,249 distinct firm–application observations filed in 2010–2024, after removal of the 737 confirmed mismatch links. Normalize application-year citations using all grant-linked applications in the sample with the same filing year and citation year, optionally also the same primary CPC3. Include zero-citation application-years from filing through 2024; set normalized values to zero when the entire cell has zero citations.</p><p>For each firm, select ultimately granted applications filed in t+1, t+2 or t+3, where t is VDyear (the existing pseudo-treatment year for non-VD firms). Sum each selected application's annual normalized citations through 2024, divide by the number of selected granted applications, and apply ln(1+x). Firms without eligible applications are assigned zero, preserving the full-firm table convention; this combines patent production and quality and is not a quality-only regression conditional on patenting.</p><p>The complete-window result restricts t≤2021. The full-sample result includes t&gt;2021 and therefore partially observed filing windows. Filing-cohort normalization adjusts relative citation opportunity within this sample; it does not recover unobserved future citations or applications that have not yet been granted.</p><p>The earlier staggered DiD used annual firm-year level sums of six outcomes: fwd_raw, fwd_norm_cohort, fwd_norm_cohort_cpc, fwd_rate, fwd_rate_norm, fwd_rate_norm_cpc. It did not use ln(1+x), per-patent division, or a three-year cross-sectional outcome. Its citation timing was incorrect; this run corrects the two requested cross-sectional measures and does not rerun the older DiD.</p></div>''')
parts.append('<pre>'+html.escape(json.dumps(q,indent=2))+'</pre></html>')
(R/'Table4_results.html').write_text('\n'.join(parts),encoding='utf-8')
assert len(d.groupby(['sample','method','model']))==16
print(d[d.term.eq('VD')][['sample','method','model','b','p','N','r2']].to_string(index=False))
