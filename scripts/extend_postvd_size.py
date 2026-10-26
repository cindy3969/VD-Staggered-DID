"""Dated post-reference-year size observations; preserve the 2,820-firm master."""
from pathlib import Path
import json, shutil
from datetime import datetime
import pandas as pd
import numpy as np

BASE=Path(__file__).resolve().parents[1]/'outputs/psm_final_2820_package'
OUT=BASE/'postvd_size_research'
NEW=[]
def add(name,metric,year,value,url,basis='reported',date='',note=''):
    NEW.append(dict(OrganizationName=name,metric=metric,observed_year=year,value=value,
        source_url=url,basis=basis,observed_date=date,note=note,retrieved_date='2026-10-20'))

add('2ULaundry','employees',2019,31,'https://www.axios.com/local/charlotte/2019/09/12/2ulaundry-raises-6-million-to-fund-expansion-now-has-5000-customers-in-charlotte-179357',date='2019-09-12')
add('Ayla Networks','employees',2018,140,'https://www.techcompanynews.com/ayla-networks-helps-companies-connect-assets-get-value-from-iot-projects/',date='2018-10-22',note='CEO interview, pre-IPO company.')
add('Citus Data','employees',2019,40,'https://www.hurriyetdailynews.com/microsoft-acquires-turkish-open-source-firm-citus-data-140768','third_party_estimate','2019-01-25','LinkedIn count reported at Microsoft acquisition; auxiliary only.')
add('Anki','employees',2019,200,'https://www.pressherald.com/2019/04/30/dreams-of-ubiquitous-social-robots-still-arent-coming-true-3/','upper_approx','2019-04-30','Nearly 200 immediately before closure; not exact.')
add('Anki','revenue',2017,100000000,'https://news.crunchbase.com/venture/robot-maker-anki-issues-series-1-shares-in-new-funding-round/','upper_approx','','Approached USD100m, not an exact point; 2018 projection excluded.')
add('Cloud Cruiser','employees',2017,50,'https://www.hpe.com/content/dam/hpe/download/pdf/newsroom/451-Report-HPE-Cloud-Cruiser-achieves-escape-velocity-to-the-HPE-sy....pdf?cc=us&ll=en','approximate','2017-01-24','About 50; acquisition announcement.')
add('Cloud Cruiser','revenue',2013,8000000,'https://www.hpe.com/content/dam/hpe/download/pdf/newsroom/451-Report-HPE-Cloud-Cruiser-achieves-escape-velocity-to-the-HPE-sy....pdf?cc=us&ll=en','lower_bound','','Exceeded USD8m; excluded from point revenue.')
add('Affirmed Networks','employees',2020,500,'https://www.geekwire.com/2020/microsoft-acquire-affirmed-networks-bolster-5g-related-cloud-offerings/','lower_bound','2020-03-26','More than 500, acquisition announcement.')
add('CloudBees','employees',2021,500,'https://www.cbinsights.com/research/cloudbees-series-f-funding/','lower_bound','2021-12-13','Over 500; not a point estimate.')
add('Emplify','employees',2021,52,'https://www.ibj.com/articles/fishers-based-software-firm-emplify-acquired-for-50-million',date='2021-04-27',note='All 52 hired by acquirer 15Five; target headcount at acquisition.')
add('Ezoic','employees',2019,100,'https://www.prnewswire.com/news-releases/ezoic-receives-33-million-in-growth-funding-to-expand-artificial-intelligence-platform-for-digital-publishers-300896761.html','approximate',note='Company press release, approximately 100.')
add('Catapult Health','revenue',2024,30000000,'https://ir.teladoc.com/news-and-events/investor-news/press-release-details/2025/Teladoc-Health-to-Acquire-Catapult-Health-Advancing-Integrated-Care-Strategy/default.aspx','TTM','2024-09-30','Approximate trailing twelve months as of Q3 2024; not calendar annual revenue.')

add('BenchPrep','employees',2019,50,'https://www.builtinchicago.org/articles/benchprep-20-million-funding-round','approximate','2019-01-15','Around 50 at financing; future doubling excluded.')
add('Donuts','employees',2021,300,'https://www.geekwire.com/2021/domain-name-registry-donuts-acquired-time-ethos-capital/','approximate','2021-04-02','About 300 across four global offices; includes prior acquisitions.')

add('Tipalti','employees',2021,720,'https://www.cbinsights.com/research/tipalti-series-f-funding/',date='2021-12-10')
add('JobNimbus','employees',2024,200,'https://www.techbuzznews.com/jobnimbus-acquires-sumoquote-2/',date='2024-01-28',note='JobNimbus headcount reported separately from SumoQuote 35; do not sum.')
add('Saviynt','employees',2024,800,'https://ionanalytics.com/insights/mergermarket/saviynt-looks-for-technology-buys-to-accelerate-growth/',date='2024-02-20',note='CEO interview; date is 2024, not revenue reference year 2023.')
for year,value in [(2018,886),(2019,1403)]:
    add('Datadog','employees',year,value,'https://www.sec.gov/Archives/edgar/data/1561550/000156459020006422/ddog-10k_20191231.htm',date=f'{year}-12-31',note='2019 10-K; 2018 pre-IPO, 2019 after IPO.')
for year,value in [(2017,100800000),(2018,198100000),(2019,362800000)]:
    add('Datadog','revenue',year,value,'https://www.sec.gov/Archives/edgar/data/1561550/000156459020006422/ddog-10k_20191231.htm','approximate',f'{year}-12-31','Annual revenue rounded to USD0.1m in filing narrative.')
for year,value,date in [(2020,2216,'2020-12-31'),(2023,3486,'2023-06-30')]:
    add('Instacart','employees',year,value,'https://www.sec.gov/Archives/edgar/data/1579091/000119312523221345/d55348ds1.htm',date=date,note='Full-time employees, excludes independent-contractor shoppers; both before IPO.')

add('CallRail','employees',2021,300,'https://www.prweb.com/releases/CallRail_Celebrates_Record_Breaking_Year_of_Growth_and_its_10th_Anniversary/prweb18422858.htm',date='2021-12-31',note='Company year-end 2021 headcount. ARR excluded from annual revenue.')
add('Moon Express','employees',2017,30,'https://www.independent.co.uk/news/long_reads/if-no-one-owns-the-moon-can-anyone-make-money-up-there-space-astronomy-a8087126.html',date='2017-12-04')
add('Enigma Technologies','employees',2019,110,'https://finovate.com/videos/finovatespring-2019-enigma/',note='Company presenter profile at FinovateSpring 2019, New York enigma.com.')
add('SpotHero','employees',2019,210,'https://techcrunch.com/2019/08/22/on-demand-parking-startup-spothero-raises-50-million/',date='2019-08-22')
add('Databox','employees',2026,63,'https://databox.com/careers',basis='current_website_snapshot',date='2026-10-20',note='63 Playmakers on company careers page; retrieval-year snapshot, not historical reconstruction.')
add('Biological Dynamics','employees',2025,51,'https://leadiq.com/c/biological-dynamics/5a1d862f2400002400608402/employee-directory','third_party_estimate','2025-06','Dated provider estimate, auxiliary only.')
add('Luminoso','employees',2025,21,'https://getlatka.com/companies/luminoso.com','third_party_estimate','2025-07','Dated provider milestone; estimation methodology unverified.')
add('Modo Labs','employees',2025,101,'https://getlatka.com/companies/modolabs.com','third_party_estimate','2025-07','Dated provider milestone.')
add('Modo Labs','employees',2024,75,'https://aventure.vc/companies/modo-labs-cambridge-ma-us?tab=company','third_party_estimate','2024-02-05')
add('Directly','employees',2024,404,'https://aventure.vc/companies/directly-san-francisco-ca-us','third_party_estimate','2024-02-05','Contractor inclusion unknown.')
add('Hiver','employees',2026,280,'https://research.crustdata.com/company/hiver','third_party_estimate','2026-09')
add('HaptX','employees',2026,11,'https://profiles.crustdata.com/company/haptx','third_party_estimate','2026-03')
add('Petcube','employees',2026,51,'https://seedtable.com/companies/petcube','third_party_estimate','2026-07-28','Provider profile update date; underlying employee observation date may differ.')
add('UrbanSitter','employees',2017,30,'https://www.thebump.com/a/lynn-perkins','lower_bound','2017-06-19','More than 30 full/part-time staff; 150000 sitters excluded.')
add('Bluevine','employees',2019,300,'https://en.globes.co.il/en/article-israel-fintech-co-bluevine-raises-102m-1001307856','lower_bound','2019-11-19','Over 300 worldwide; Tel Aviv subset100 not added.')
add('Rollbar','employees',2020,80,'https://www.businesswire.com/news/home/20201118005349/en/Rollbar-Lets-Developers-Focus-on-Continuously-Improving-Code-with-AI-Assisted-Workflows-and-Automation-Grade-Grouping','lower_bound','2020-11-18','More than 80, up from40 earlier in2020; exact month of40 unspecified.')

add('Bitmovin','employees',2021,160,'https://www.forbes.com/sites/travisbean/2021/06/11/bitmovin-is-building-a-better-future-for-streaming-movies-and-shows-at-home/',date='2021-06-11',note='CEO interview; worldwide company staff.')
add('DroneDeploy','employees',2026,383,'https://leadiq.com/c/dronedeploy/5a1d87f2240000240061ce46','third_party_estimate','2026-08')
add('Rentable','employees',2026,156,'https://leadiq.com/c/rentable/5a1d8a6a240000240063c652','third_party_estimate','2026-07','Madison former ABODO; not Boston security-deposit company.')

def main():
    dta=BASE/'table3_current_2820_cross_section_v2.dta'
    csv=dta.with_suffix('.csv')
    with pd.io.stata.StataReader(dta) as rd:
        labels=rd.variable_labels(); vl=rd.value_labels(); label=rd.data_label
        original=rd.read(convert_categoricals=False)
        values={v:vl[l] for v,l in zip(rd._varlist,rd._lbllist) if l in vl}
    assert len(original)==2820 and original.firm_id.is_unique
    web=pd.read_csv(OUT/'web_observations.csv').drop(columns=['firm_id','VDyear','rel_year','in_window'],errors='ignore')
    web=pd.concat([web,pd.DataFrame(NEW)],ignore_index=True).drop_duplicates(['OrganizationName','metric','observed_year','value','source_url'])
    web=web.merge(original[['firm_id','OrganizationName','VDyear']],on='OrganizationName',validate='many_to_one')
    web['t']=web.observed_year-web.VDyear
    web['eligible_point']=web.basis.isin(['reported','approximate','management_claim','current_website_snapshot']) & web.metric.isin(['employees','revenue']) & web.t.gt(0)
    web.to_csv(OUT/'web_observations_extended.csv',index=False)
    pb=pd.read_csv(OUT/'pb_matched_all_records.csv',low_memory=False)
    pb=pb[pb.rel_year.gt(0)&pb.fiscalyear.le(2026)&pb.revenue.notna()]
    records=[]; conflicts=[]
    for (fid,year),g in pb.groupby(['firm_id','fiscalyear']):
        vals=g.revenue.round(6).unique()
        if len(vals)!=1:
            conflicts.append(dict(firm_id=fid,year=year,values=';'.join(map(str,vals)),source_rows=';'.join(g.source_row.astype(str))))
            continue
        records.append(dict(firm_id=fid,year=int(year),metric='revenue',value=float(vals[0])*1e6,
            source='pb_deal_finance.csv rows '+','.join(g.source_row.astype(str)),basis='PB USDm inferred; fiscalyear; annual/TTM unverified',date='',priority=1))
    # Start with existing selected t1-t3 values to preserve prior curated observations.
    for _,r in original.iterrows():
        for t in (1,2,3):
            for metric in ('employees','revenue'):
                if pd.notna(r[f'{metric}_t{t}']):
                    records.append(dict(firm_id=r.firm_id,year=int(r.VDyear+t),metric=metric,value=r[f'{metric}_t{t}'],source=r[f'{metric}_src_t{t}'],basis=r[f'{metric}_basis_t{t}'],date=r[f'{metric}_date_t{t}'],priority=2))
    for _,r in web[web.eligible_point].iterrows():
        records.append(dict(firm_id=r.firm_id,year=int(r.observed_year),metric=r.metric,value=r.value,source=r.source_url,basis=r.basis,date=r.observed_date if pd.notna(r.observed_date) else '',priority=3))
    obs=pd.DataFrame(records)
    # New verified web points supersede same-year existing selections; never pick largest.
    obs=obs.sort_values(['firm_id','year','metric','priority'],kind='stable').drop_duplicates(['firm_id','year','metric'],keep='last')
    ids=obs[['firm_id','year']].drop_duplicates()
    for metric in ['employees','revenue']:
        g=obs[obs.metric.eq(metric)].drop(columns=['metric','priority']).rename(columns={c:f'{metric}_{c}' for c in ['value','source','basis','date']})
        ids=ids.merge(g,on=['firm_id','year'],how='left',validate='one_to_one')
    panel=ids.merge(original,on='firm_id',validate='many_to_one')
    panel['t']=panel.year-panel.VDyear
    assert panel.t.gt(0).all() and not panel.duplicated(['firm_id','year']).any()
    panel=panel.rename(columns={'employees_value':'employees','revenue_value':'revenue_usd'})
    # Cross-sectional convenience fields: earliest available post-year, not pooled or summed.
    result=original.copy()
    for metric in ('employees','revenue'):
        g=obs[obs.metric.eq(metric)].sort_values(['year','firm_id']).drop_duplicates('firm_id').set_index('firm_id')
        for suffix,field in [('post','value'),('post_year','year'),('post_src','source'),('post_basis','basis'),('post_date','date')]:
            c=f'{metric}_{suffix}'
            result[c]=result.firm_id.map(g[field])
            if field in ['source','basis','date']: result[c]=result[c].fillna('')
            labels[c]=(f'{metric}: earliest dated post-VD observation; {suffix}')[:80]
        result[f'{metric}_post_t']=result[f'{metric}_post_year']-result.VDyear
        result[f'{metric}_post_nyears']=result.firm_id.map(obs[obs.metric.eq(metric)].groupby('firm_id').year.nunique()).fillna(0).astype('int32')
        for t in (1,2,3):
            g=panel[panel.t.eq(t)].set_index('firm_id')
            val='employees' if metric=='employees' else 'revenue_usd'
            mask=result.firm_id.isin(g[g[val].notna()].index)
            for dest,source in [(f'{metric}_t{t}',val),(f'{metric}_year_t{t}','year'),(f'{metric}_src_t{t}',f'{metric}_source'),(f'{metric}_basis_t{t}',f'{metric}_basis'),(f'{metric}_date_t{t}',f'{metric}_date')]:
                result.loc[mask,dest]=result.loc[mask,'firm_id'].map(g[source]).values
        result[f'{metric}_nyears']=result[[f'{metric}_t{t}' for t in (1,2,3)]].notna().sum(axis=1)
    for frame in (result,panel):
        for c in frame.select_dtypes(include=['object','str']): frame[c]=frame[c].fillna('').astype(str)
    changed={c for c in result if c not in original or not result[c].equals(original[c])}
    allowed={c for c in result if c.startswith(('employees_','revenue_'))}
    assert changed<=allowed, changed-allowed
    for c in original:
        if c not in changed: pd.testing.assert_series_equal(original[c],result[c])
    stage=OUT/'extended_validated.dta'
    result.to_stata(stage,write_index=False,version=118,variable_labels={k:v for k,v in labels.items() if k in result},value_labels=values,data_label=label)
    pd.testing.assert_frame_equal(result,pd.read_stata(stage,convert_categoricals=False),check_dtype=False)
    oldcsv=pd.read_csv(csv)
    csvresult=oldcsv.drop(columns=[c for c in changed if c in oldcsv]).merge(result[['firm_id']+sorted(changed)],on='firm_id',validate='one_to_one',sort=False)
    csvresult.to_csv(OUT/'extended_validated.csv',index=False)
    backup=BASE/'backups'/('before_extended_size_'+datetime.now().strftime('%Y%m%d_%H%M%S')); backup.mkdir(parents=True)
    for f in (dta,csv): shutil.copy2(f,backup/f.name)
    shutil.copy2(stage,dta); shutil.copy2(OUT/'extended_validated.csv',csv)
    # Save the full firm-year file with all master covariates for pooled regressions.
    panel.to_csv(OUT/'postvd_size_all_years.csv',index=False)
    panel.to_stata(OUT/'postvd_size_all_years.dta',write_index=False,version=118,value_labels=values)
    pd.DataFrame(conflicts).to_csv(OUT/'pb_all_years_revenue_conflicts.csv',index=False)
    stats={m:dict(firms=int(result[f'{m}_post'].notna().sum()),firm_years=int(result[f'{m}_post_nyears'].sum()),t1_t3_firms=int(result[f'{m}_nyears'].gt(0).sum()),t1_t3_observations=int(result[f'{m}_nyears'].sum())) for m in ['employees','revenue']}
    stats.update(backup=str(backup),web_new_records=len(NEW),all_firms_web_searched=False,panel_rows=len(panel))
    (OUT/'extended_summary.json').write_text(json.dumps(stats,indent=2),encoding='utf8')
    print(json.dumps(stats,indent=2))

if __name__=='__main__': main()
