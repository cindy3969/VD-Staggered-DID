"""Measurement validation only. Preserve the authoritative matched sample and VD coding."""
from pathlib import Path
import pandas as pd
import numpy as np
import re, json, hashlib, html, os, sys

ROOT=Path(os.environ.get('VD_PROJECT_ROOT','C:/Users/user/Documents/VD'))
OUT=ROOT/'outputs/vd_lender_validation_2820'
OUT.mkdir(exist_ok=True)
SOURCE=Path('C:/Users/user/iCloudDrive/5학기/연구미팅/20240108-2010 to 2015 firms/2010 2015 Crunchbase deals merged_v4.xlsx')
SAMPLE=ROOT/'outputs/psm_final_2820_package/table3_current_2820_cross_section_v2.dta'
GUIDE='https://ctinnovations.com/wp-content/uploads/2017/06/Bessemer-Guide-to-Venture-Debt.pdf'
registry={}
def add(names,cat,sub,url,note):
    for name in names.split('|'):
        registry[name]={'category':cat,'subtype':sub,'source_url':url,'classification_basis':note,'review_status':'public_source_reviewed'}

# A conservative institutional taxonomy. Revenue-based/asset-backed credit is category 3,
# not automatically conventional venture debt. Current websites establish provider identity,
# not the historical contract terms of each source transaction.
add('Hercules Capital',1,'venture_debt','https://www.htgc.com/','Specialist venture lender')
add('Western Technology Investment',1,'venture_debt','https://www.westerntech.com/','Debt capital for startups since 1980')
add('Horizon Technology Finance',1,'venture_debt','https://horizontechfinance.com/about-us/the-horizon-story/','Structured venture lending to technology and life science companies')
add('Trinity Capital',1,'venture_growth_debt','https://ir.trinitycapital.com/investor-relations/','Growth capital provider; also equipment and asset-based lending')
add('Oxford Finance LLC',1,'life_science_growth_debt','https://oxfordfinance.com/','Innovation/life-science lending; other lending products also offered')
add('Runway Growth Capital',1,'venture_growth_debt','https://runwaygrowth.com/','Debt financing for late and growth stage companies')
add('Espresso Capital',1,'venture_growth_debt','https://espressocapital.com/about/','Venture debt provider founded in 2009')
add('TriplePoint Capital|TriplePoint Venture Growth',1,'venture_growth_debt','https://www.triplepointcapital.com/','Debt financing for venture-backed companies')
add('Kreos Capital|Lighthouse Capital Partners|Escalate Capital Partners|Wellington Financial',1,'venture_growth_debt',GUIDE,'Named in historical venture lender guide, Appendix A')
add('Columbia Lake Partners',1,'venture_debt','https://clpgrowth.com/','Growth loans to technology companies')
add('Eastward Capital Partners',1,'venture_debt','https://eastwardcp.com/','Venture debt to venture-backed technology companies')
add('ORIX Growth Capital',1,'venture_growth_debt','https://www.orix.com/private-credit/growth-capital/','Dedicated growth lending and venture debt business')
add('Structural Capital',1,'venture_growth_debt','https://structuralcapital.com/lending-philosophy/','Technology growth debt and runway financing')
add('K2 HealthVentures',1,'life_science_growth_debt','https://k2hv.com/','Customized debt for innovative life science companies')
add('Viola Credit',1,'venture_growth_and_asset_backed','https://www.viola-group.com/violanotes/viola-credit-founder-ruthi-simha-on-the-benefits-of-venture-lending-and-on-being-a-woman-in-a-male-dominated-industry/','Venture lending arm; also asset-backed facilities, so deal purpose remains unverified')
add('Partners for Growth',1,'venture_growth_debt','https://www.sec.gov/comments/s7-41-11/s74111-147.pdf','Provider describes debt to emerging technology and life science companies')
add('Agility Capital',1,'emerging_growth_debt','https://agilitycap.com/team','Debt products for emerging growth companies')
add('LunaCap Ventures',1,'venture_debt','https://www.lunacapventures.com/','Explicit venture-debt strategy; also other capital products')
add('Claret Capital Partners',1,'venture_growth_debt','https://www.claret-capital.com/','Independent growth debt fund manager')
add('Silicon Valley Bank',2,'venture_bank','https://www.svb.com/business-banking/lending/venture-debt/','Established venture debt operation; historical identity retained')
add('Bridge Bank',2,'venture_bank','https://www.westernalliancebancorporation.com/expertise/innovation-banking','Bridge Bank innovation banking and venture debt')
add('Square 1 Bank|Pacific Western Bank|PacWest Bancorp',2,'venture_bank','https://www.sec.gov/Archives/edgar/data/1329799/000110465915015453/a15-5667_1ex99d1.htm','Historical Square 1/Pacific Western venture banking franchise')
add('Comerica Incorporated',2,'venture_bank','https://www.comerica.com/business/industry-solutions/specialized-industries/technology.html','Established technology and life science venture lending')
add('City National Bank',2,'venture_bank',GUIDE,'Bank listed in historical venture lender guide, Appendix A')
add('CIBC Innovation Banking',2,'venture_bank','https://cibc.mediaroom.com/2018-01-08-CIBC-Innovation-Banking-launches-to-serve-North-American-companies','Innovation banking launched in 2018 after Wellington acquisition')
add('Lighter Capital',3,'revenue_based_credit','https://www.lightercapital.com/how-it-works','Revenue-based/term loans; institutional debt, not automatically conventional VD')
add('Novel Capital',3,'revenue_based_financing','https://novelcapital.com/revenue-based-financing-101/','Revenue financing distinct from conventional venture debt; contract form not checked')
add('TIMIA Capital',3,'revenue_based_credit','https://timiacapital.com/get-funded/','SaaS revenue-based and term debt')
add('Bigfoot Capital',3,'software_growth_credit','https://bigfootcap.com/blog/what-do-saas-investors-look-for-in-the-companies-they-invest-in','Revenue-underwritten software loans; distinguishes itself from pure venture debt')
add('SaaS Capital',3,'recurring_revenue_credit','https://www.saas-capital.com/','SaaS recurring revenue lending')
add('Recurring Capital Partners',3,'software_growth_credit','https://recurring.capital/','Software growth debt')
add('Montage Capital',3,'growth_credit','https://www.montagecapital.com/home-edits-copy','Growth debt for capital-efficient businesses')
add('WindSail Capital Group',3,'clean_energy_growth_credit','https://windsailcapital.com/','Flexible debt for clean energy growth; not necessarily VC-backed VD')
add('Advantage Capital',3,'institutional_debt_equity','https://www.advantagecap.com/small-business/connecticut/','Debt and equity provider; individual role not independently verified')
add('Dwight Funding',3,'asset_based_credit','https://dwightfunding.com/','Asset-based and recurring-revenue lines')
add('Community Investment Management',3,'asset_backed_fintech_credit','https://cim-llc.com/approach','Receivables-backed debt for fintech lenders')
add('Victory Park Capital',3,'asset_backed_credit','https://www.victoryparkcapital.com/','Institutional asset-backed credit')
add('Vista Credit Partners',3,'technology_private_credit','https://www.vistaequitypartners.com/credit/','Software/technology private credit; conventional VD not established')
add('Golub Capital',3,'direct_lending','https://golubcapital.com/about/about-us/','Institutional direct lending')
add('CRG',3,'healthcare_private_credit','https://crglp.com/about','Healthcare private credit')
add('Perceptive Advisors',3,'healthcare_credit_and_equity','https://www.perceptivelife.com/credit-opportunities','Credit opportunities strategy; exact transaction role not checked')
add('Ares Management',3,'private_credit','https://www.aresmgmt.com/about-ares-management-corporation/our-team/katherine-rendleman?pid=178142','Institutional direct-lending business')
add('BlackRock',3,'diversified_credit_manager','https://www.blackrock.com/institutions/en-us/investment-capabilities/strategies/private-credit','Parent platform not treated as equivalent to its Kreos subsidiary')
add('Armentum Partners',4,'debt_adviser','https://armentumpartners.com/financial-services/','Debt adviser arranging lenders; its name alone does not identify the lender')
add('Trifecta Capital Advisors',1,'venture_debt','https://www.trifectacapital.in/venture-debt','Dedicated venture debt strategy')
add('Stride Ventures',1,'venture_debt','https://strideventures.global/reports','Provider publishes its venture debt strategy and reports')
add('ATEL Growth Capital',1,'venture_debt_equipment','https://atel.com/company','Venture debt and equipment leasing; deal-level product not verified')
add('HSBC Innovation Banking',2,'venture_bank','https://www.about.us.hsbc.com/newsroom/press-releases/hsbc-us-innovation-banking-expands-venture-debt-offering','Dedicated US operation expanded 2023; late-stage lending since 2019')
add('Avidbank',2,'venture_bank','https://ir.avidbank.com/files/doc_downloads/Rule-144-Public-Info-09-30-24.pdf','Bank describes dedicated venture lending division')
add('JP Morgan|JP Morgan Chase',2,'venture_bank','https://www.jpmorganchase.com/content/dam/jpmc/jpmorgan-chase-and-co/investor-relations/documents/events/2023/jpmc-investor-day-2023/commercial-banking.pdf','2023 presentation describes early-stage lending; provider classification only, historical contract unverified')
add('Barclays Corporate Banking',2,'venture_bank',GUIDE,'Barclays bank franchise in historical venture lender guide; individual deal purpose unverified')
add('Multiplier Capital',1,'venture_growth_debt','https://www.multipliercapital.com/','Historical provider announcement identifies venture debt strategy')
add('Brex Venture Debt',1,'venture_debt','https://www.sec.gov/Archives/edgar/data/1890347/000095014221003374/xslFormDX01/primary_doc.xml','SEC filing identifies dedicated Brex Venture Debt Fund I in 2021')
add('Flow Capital',1,'venture_growth_debt','https://www.flowcap.com/for-founders','Dedicated growth venture debt; contract form remains deal-specific')
add('Vistara Growth',3,'software_growth_credit','https://vistaragrowth.com/insights/growth-debt-versus-venture-debt/','Provider differentiates growth debt from conventional venture debt')
add('Cypress Growth Capital',3,'royalty_based_credit','https://www.cypressgrowthcapital.com/?c=51958221','Royalty-based capital structured as flexible debt')
add('Feenix Venture Partners LLC',3,'institutional_credit','https://www.sec.gov/Archives/edgar/data/1567900/000143774920023965/ex_213796.htm','SEC-filed credit agreement identifies Feenix lending vehicle')
add('Capital IP Investment Partners LP',3,'structured_technology_credit','https://www.linkedin.com/company/capital-ip-investment-partners','Provider profile describes structured debt and hybrid capital')
add('LIQUiDITY Group|Mars Growth Capital',3,'technology_growth_credit','https://www.liquidity.com/press-release/global-expansion---liquidity-group-deploys-1-6b-in-over-65-countries-in-2022','Growth credit platform and MARS vehicle; conventional VD product not assumed')
add('MidCap Financial',3,'diversified_specialty_finance','https://www.midcapfinancial.com/','Direct lender with multiple products including venture finance; exact unit not identified')
add('SLR Capital Partners|SLR Investment|Solar capital',3,'diversified_specialty_finance','https://www.slrcapitalpartners.com/','Diversified cash-flow and asset-based lending platform')
add('Fortress Investment Group',3,'private_credit','https://www.fortress.com/what-we-do','Diversified institutional credit platform')

def split_names(x):
    if pd.isna(x) or not str(x).strip(): return []
    parts=re.split(r',\s*',str(x).strip())
    out=[]
    for p in parts:
        if p in ('LLC','LLP','LP','L.P.','Inc.','Inc','Ltd.','Ltd') and out: out[-1]+=', '+p
        elif p.strip(): out.append(p.strip())
    return list(dict.fromkeys(out))

if __name__=='__main__':
    f=pd.read_stata(SAMPLE,convert_categoricals=False)
    assert len(f)==2820 and f.firm_id.is_unique and f.OrganizationName.is_unique
    cache=ROOT/'outputs/lender_source_cache.pkl'
    d=pd.read_pickle(cache) if '--use-session-cache' in sys.argv and cache.exists() else pd.read_excel(SOURCE,header=1)
    d['source_excel_row']=np.arange(len(d))+3
    m=d.merge(f[['firm_id','OrganizationName','VD','VDyear','Foundingyear','Region2','Industry2','earlystage','MoneyRaised_VD','NumofFundingRounds_VD']],left_on='Organization Name',right_on='OrganizationName',suffixes=('_source',''),validate='many_to_one')
    assert m.firm_id.nunique()==2820
    q=m[m.Debt.eq(1)|m['Funding Type'].eq('Debt Financing')].copy()
    q['participants']=q['Investor names'].map(split_names)
    allnames=sorted(set(n for ns in q.participants for n in ns))
    # No name-based promotion of a VC, angel, adviser or unverified entity to lender.
    for n in allnames:
        if n not in registry:
            registry[n]={'category':4,'subtype':'unresolved_participant_role','source_url':'','classification_basis':'Named participant in source; lender role and provider type not established','review_status':'unresolved_not_individually_web_verified'}
    # Clear bank names can support an institutional identity classification from the source.
    # These are kept distinct from externally reviewed venture-lending franchises.
    banks='Goldman Sachs|Goldman Sachs Bank USA|Goldman Sachs Asset Management|Goldman Sachs Urban Investment Group|Credit Suisse|Deutsche Bank|East West Bank|Cadence Bancorp|SunTrust Bank|CIT Group|CIT Healthcare Finance|Wells Fargo Capital Finance|Wells Fargo|Wells Fargo Securities|KeyBanc Capital Markets|Keybank|Barclays Investment Bank|Regions Bank|Webster Bank|Citi|Fifth Third Bank|BHI|Bank of America|Bank of America Merrill Lynch|HSBC|HSBC Bank|RBC Capital Markets|MUFG Bank|Mitsubishi UFJ Financial Group|Sumitomo Mitsui Banking Corporation|Capital One|Natixis|Morgan Stanley|Morgan Stanley Renewables|ING Capital LLC|ING Group|TD Securities|WebBank|CIBC|Ally Financial|CoBank|TD Bank|ConnectOne Bank|Wintrust Financial|Citizens Bank|Umpqua Bank|National Australia Bank (NAB)|PNC Bank|Sallfort Privatbank AG|Cathay Bank|Signature Bank|BBVA USA|DZ BANK|Green Bank|Commerzbank|Intesa Sanpaolo|Santander|The Bancorp|Opus Bank|Bank Leumi|Cross River Bank|Sterling National Bank|Cambridge Trust Company|Citibank Europe|Mizuho Bank|Toronto Dominion Bank Group|MUFG Union Bank|Investec|Nord/LB|Gorham Savings Bank|Forbright Bank|Grasshopper Bank|Shinhan Bank|Royal Bank of Canada|Societe Generale|Truist'.split('|')
    for n in banks:
        if n in allnames and registry[n]['category']==4:
            registry[n]={'category':3,'subtype':'bank_or_banking_group','source_url':'','classification_basis':'Recognizable banking institution named in source debt round; specific lending unit and historical deal role unverified','review_status':'source_identity_classification_not_external_deal_verification'}
    public_pattern=r'Government|Department of Energy|Economic Development|MassDevelopment|Maine Technology Institute|Massachusetts Life Sciences|North Carolina Biotechnology|Ben Franklin Technology|TEDCO|Connecticut Innovations|New York Ventures|Finance Authority|FedDev|Invest Victoria|ENISA|CDTI|Keyhorse Capital|Invest Nebraska|European Investment Bank|International Finance Corporation|NY Green Bank|Connecticut Green Bank|Florida Institute for the Commercialization'
    for n in allnames:
        if re.search(public_pattern,n,re.I):
            registry[n].update(category=4,subtype='public_or_development_finance_review',government_review=1,classification_basis='Public/development-program identity indicator; verify exclusion rule and whether transaction is guaranteed, direct public lending, or investment. No automatic recode.')
    # Additional reviewed mappings can be maintained without altering the raw workbook.
    extra=OUT/'additional_provider_evidence.json'
    if extra.exists(): registry.update(json.loads(extra.read_text(encoding='utf-8')))
    q['cb_debt_type']=q['Funding Type'].eq('Debt Financing').astype(int)
    q['named_participant']=q.participants.map(bool).astype(int)
    for c in range(1,5): q[f'has_cat{c}']=q.participants.map(lambda ns:int(any(registry[n]['category']==c for n in ns)))
    q['provider_cat']=q.participants.map(lambda ns:min([registry[n]['category'] for n in ns],default=0))
    q['type_conflict']=(~q['Funding Type'].eq('Debt Financing')).astype(int)
    q['deal_category']=q.provider_cat.where(q.type_conflict.eq(0),4)
    q['government_review']=q.participants.map(lambda ns:int(any(registry[n].get('government_review',0) for n in ns)))
    q['adviser_present']=q.participants.map(lambda ns:int(any(registry[n]['subtype']=='debt_adviser' for n in ns)))
    q['first_vd_source']=q['First VD'].eq(1).astype(int)
    q['year_mismatch']=(q.first_vd_source.eq(1)&q['Deal year'].ne(q.VDyear)).astype(int)
    q['deal_date']=pd.to_datetime(q['Announced Date'],errors='coerce')
    m['date']=pd.to_datetime(m['Announced Date'],errors='coerce')
    eqmask=m['Funding Type'].str.match(r'^Series [A-Z]',na=False)
    seedmask=m['Funding Type'].isin(['Seed','Pre-Seed','Angel'])
    groups={i:g for i,g in m.groupby('firm_id')}
    for col in ['prior_series_rounds','prior_seed_angel_rounds','same_day_series','later_series_rounds','prior_named_series_rounds','days_since_series','prior_series_usd']:
        q[col]=np.nan
    for idx,r in q.iterrows():
        g=groups[r.firm_id]; dt=r.deal_date
        series=g[g['Funding Type'].str.match(r'^Series [A-Z]',na=False)]
        prior=series[series.date.lt(dt)]
        q.loc[idx,['prior_series_rounds','prior_seed_angel_rounds','same_day_series','later_series_rounds','prior_named_series_rounds','days_since_series','prior_series_usd']]=[
            len(prior),int((g.date.lt(dt)&g['Funding Type'].isin(['Seed','Pre-Seed','Angel'])).sum()),int(series.date.eq(dt).sum()),int(series.date.gt(dt).sum()),int(prior['Investor names'].notna().sum()),(dt-prior.date.max()).days if len(prior) else np.nan,prior['Money Raised Currency (in USD)'].sum(min_count=1)]
    q['amount_reported']=(pd.to_numeric(q['Money Raised Currency (in USD)'],errors='coerce')>0).astype(int)
    q['date_reported']=q.deal_date.notna().astype(int)
    q['issuer_age']=q['Deal year']-q.Foundingyear
    q['ipo_before_deal']=(pd.to_datetime(q['IPO Date'],errors='coerce').le(q.deal_date)).astype(int)
    known_ids=set(q.loc[q.deal_category.isin([1,2])&q.cb_debt_type.eq(1),'firm_id'])
    q['same_firm_specialist_bank']=q.firm_id.isin(known_ids).astype(int)
    q['anonymous_evidence']=np.where(q.named_participant.eq(1),'not_anonymous',np.where(q.prior_series_rounds.gt(0),'debt_label_plus_prior_series',np.where(q.prior_seed_angel_rounds.gt(0)|q.same_day_series.gt(0),'debt_label_plus_seed_or_same_day_series','debt_label_no_prior_equity_observed')))
    q['strict_lender_support']=(q.cb_debt_type.eq(1)&q.deal_category.isin([1,2])&q.government_review.eq(0)&q.ipo_before_deal.eq(0)).astype(int)
    q['strict_context_support']=(q.strict_lender_support.eq(1)&q.prior_series_rounds.gt(0)).astype(int)
    # Provider presence is not transaction verification. Retain a dated public exception.
    q['external_deal_evidence']=''
    q.loc[q.OrganizationName.eq('Cellink')&q['Deal year'].eq(2023),'external_deal_evidence']='https://www.cellinktechnologies.com/news/cellink-corp-awarded-atvm-loan'
    from vd_external_deal_evidence import rows as webrows
    web=pd.DataFrame(webrows,columns=['OrganizationName','source_deal_date','external_amount_usd','debt_form','finding','external_participants','source_url','match_basis','noncore_review'])
    q['external_debt_form']='not_reviewed'; q['external_noncore_review']=0
    for _,wr in web.iterrows():
        sel=q.OrganizationName.eq(wr.OrganizationName)&q.deal_date.eq(pd.Timestamp(wr.source_deal_date))
        assert sel.sum()==1,wr.OrganizationName
        q.loc[sel,['external_deal_evidence','external_debt_form','external_noncore_review']]=[wr.source_url,wr.debt_form,wr.noncore_review]
        web.loc[wr.name,'source_excel_row']=int(q.loc[sel,'source_excel_row'].iloc[0])
        web.loc[wr.name,'source_amount_usd']=q.loc[sel,'Money Raised Currency (in USD)'].iloc[0]
        web.loc[wr.name,'source_name_missing']=int(q.loc[sel,'named_participant'].iloc[0]==0)
    web.to_csv(OUT/'public_deal_checks.csv',index=False,encoding='utf-8-sig')
    q['duplicate_record']=q.duplicated(['firm_id','Announced Date','Funding Type','Money Raised Currency (in USD)','Investor names'],keep=False).astype(int)
    q['participant_categories']=q.participants.map(lambda ns:'; '.join(f'{n}: {registry[n]["category"]}' for n in ns))
    q['source_row_id']=q.source_excel_row.map(lambda x:f'Sheet1!{x}')

    # One row per firm, including every control; no reclassification of original VD.
    ff=f[['firm_id','OrganizationName','VD','VDyear','Foundingyear','Region2','Industry2','earlystage','MoneyRaised_VD','NumofFundingRounds_VD']].copy()
    records=[]
    for _,r in ff.iterrows():
        g=q[q.firm_id.eq(r.firm_id)]
        first=g[g.first_vd_source.eq(1)]
        rec={'firm_id':r.firm_id,'debt_candidate_n':len(g),'cb_debt_n':int(g.cb_debt_type.sum()),'named_deal_n':int(g.named_participant.sum()),'anonymous_deal_n':int(g.named_participant.eq(0).sum()),'any_named':int(g.named_participant.any()),'only_anonymous':int(len(g)>0 and not g.named_participant.any()),'first_named':int(first.named_participant.any()),'first_source_n':len(first),'firm_category':int(g.deal_category[g.deal_category.gt(0)].min()) if g.deal_category.gt(0).any() else 0,'first_category':int(first.deal_category[first.deal_category.gt(0)].min()) if first.deal_category.gt(0).any() else 0,'strict_lender_support':int(g.strict_lender_support.any()),'first_lender_support':int(first.strict_lender_support.any()),'strict_context_support':int(g.strict_context_support.any()),'first_context_support':int(first.strict_context_support.any()),'government_review':int(g.government_review.any()),'type_conflict':int(g.type_conflict.any()),'year_mismatch':int(g.year_mismatch.any()),'ipo_before_deal':int(g.ipo_before_deal.any()),'anon_prior_series':int(((g.named_participant.eq(0))&g.prior_series_rounds.gt(0)).any()),'anon_seed_or_same_day':int((g.anonymous_evidence.eq('debt_label_plus_seed_or_same_day_series')).any()),'first_prior_series':int(first.prior_series_rounds.gt(0).any()),'first_amount_reported':int(first.amount_reported.any()),'first_date_reported':int(first.date_reported.any()),'matched_source_url':groups[r.firm_id]['Organization Name URL'].iloc[0]}
        records.append(rec)
    ff=ff.merge(pd.DataFrame(records),on='firm_id',validate='one_to_one')
    ff['external_noncore_review']=ff.firm_id.isin(q.loc[q.external_noncore_review.eq(1),'firm_id']).astype(int)
    # Non-overlapping firm evidence groups preserve uncertainty rather than relabeling treatment.
    ff['validation_group']=np.select([ff.VD.eq(0),ff.type_conflict.eq(1)&ff.cb_debt_n.eq(0),ff.strict_lender_support.eq(1),ff.firm_category.eq(3),ff.only_anonymous.eq(1)&ff.anon_prior_series.eq(1),ff.only_anonymous.eq(1)],['control','source_type_conflict','specialist_or_venture_bank','other_institutional','anonymous_prior_series','anonymous_other'],default='named_ambiguous')
    lr=[]
    for n in allnames:
        gg=q[q.participants.map(lambda ns:n in ns)]
        lr.append({'participant_name':n,**registry[n],'deal_n':len(gg),'firm_n':gg.firm_id.nunique(),'first_deal_n':int(gg.first_vd_source.sum())})
    lenders=pd.DataFrame(lr).sort_values(['category','deal_n'],ascending=[True,False])
    keep=['firm_id','OrganizationName','VD','VDyear','source_excel_row','deal no','deal_date','Deal year','Funding Type','Funding Type.1','Debt','first_vd_source','Investor names','Lead Investors','Money Raised Currency (in USD)','Number of Investors','deal_category','provider_cat','has_cat1','has_cat2','has_cat3','has_cat4','named_participant','cb_debt_type','type_conflict','government_review','adviser_present','year_mismatch','ipo_before_deal','prior_series_rounds','prior_named_series_rounds','prior_seed_angel_rounds','same_day_series','later_series_rounds','days_since_series','prior_series_usd','amount_reported','date_reported','issuer_age','same_firm_specialist_bank','anonymous_evidence','strict_lender_support','strict_context_support','duplicate_record','participant_categories','Organization Name URL','external_deal_evidence']
    deals=q[keep].copy()
    deals['external_debt_form']=q.external_debt_form
    deals['external_noncore_review']=q.external_noncore_review
    for name,df in [('firm_validation_2820',ff),('deal_validation',deals),('provider_dictionary',lenders)]: df.to_csv(OUT/f'{name}.csv',index=False,encoding='utf-8-sig')
    ff.to_stata(OUT/'firm_validation_2820.dta',write_index=False,version=118)
    ff[ff.type_conflict.eq(1)|ff.year_mismatch.eq(1)|ff.government_review.eq(1)|ff.ipo_before_deal.eq(1)|ff.external_noncore_review.eq(1)].to_csv(OUT/'firm_review_queue.csv',index=False,encoding='utf-8-sig')
    q[q.named_participant.eq(0)][keep].to_csv(OUT/'anonymous_deal_evidence.csv',index=False,encoding='utf-8-sig')
    labels={0:'No participant identity',1:'Specialized venture-debt provider',2:'Bank with venture/startup lending',3:'Other identifiable institutional lender',4:'Ambiguous'}
    summary=[]
    def metric(section,label,value,denom=None): summary.append({'section':section,'metric':label,'count':int(value),'denominator':denom,'share':value/denom if denom else None})
    metric('Sample','Matched firms',len(ff),2820); metric('Sample','VD firms',int(ff.VD.sum()),2820)
    for label,val in [('Named at any candidate deal',ff.any_named.sum()),('Only anonymous candidate deals',ff.only_anonymous.sum()),('Named at first source VD deal',ff.first_named.sum()),('Strict lender support at any debt deal',ff.strict_lender_support.sum()),('Strict lender support at first source VD deal',ff.first_lender_support.sum()),('Strict lender + prior Series context at first deal',ff.first_context_support.sum())]: metric('VD firms',label,val,1410)
    for cat,label in labels.items():
        metric('Deal categories',label,q.deal_category.eq(cat).sum(),len(q))
        metric('Firm categories (hierarchical)',label,((ff.VD.eq(1))&ff.firm_category.eq(cat)).sum(),1410)
        metric('First-deal categories',label,q.loc[q.first_vd_source.eq(1),'deal_category'].eq(cat).sum(),1410)
    anon=q[q.named_participant.eq(0)]; af=ff[ff.only_anonymous.eq(1)]
    for label,val in [('Anonymous deals',len(anon)),('Prior Series round observed',anon.prior_series_rounds.gt(0).sum()),('Seed/angel or same-day Series only',anon.anonymous_evidence.eq('debt_label_plus_seed_or_same_day_series').sum()),('No prior equity observed',anon.anonymous_evidence.eq('debt_label_no_prior_equity_observed').sum()),('Positive amount disclosed',anon.amount_reported.sum()),('Date disclosed',anon.date_reported.sum()),('Specialist/bank identified in another deal',anon.same_firm_specialist_bank.sum()),('Anonymous-only firms with prior Series',af.anon_prior_series.sum())]: metric('Anonymous evidence',label,val,len(anon) if not label.startswith('Anonymous-only') else len(af))
    firstanon=anon[anon.first_vd_source.eq(1)]
    for label,val in [('Prior Series round observed',firstanon.prior_series_rounds.gt(0).sum()),('Seed/angel or same-day Series only',firstanon.anonymous_evidence.eq('debt_label_plus_seed_or_same_day_series').sum()),('No prior equity observed',firstanon.anonymous_evidence.eq('debt_label_no_prior_equity_observed').sum()),('Positive amount disclosed',firstanon.amount_reported.sum()),('Date disclosed',firstanon.date_reported.sum())]: metric('Anonymous first deals',label,val,len(firstanon))
    for label,col in [('Funding-type conflict','type_conflict'),('Government/public-program review','government_review'),('First VD year mismatch','year_mismatch'),('IPO on/before debt date','ipo_before_deal'),('Possible duplicate record','duplicate_record')]: metric('Deal review flags',label,q[col].sum(),len(q))
    sm=pd.DataFrame(summary); sm.to_csv(OUT/'summary.csv',index=False,encoding='utf-8-sig')
    missing_compare=ff[ff.VD.eq(1)].groupby('any_named').agg(firms=('firm_id','size'),median_vd_year=('VDyear','median'),median_founding_year=('Foundingyear','median'),median_funding_usd=('MoneyRaised_VD','median'),median_rounds=('NumofFundingRounds_VD','median'),early_stage_share=('earlystage','mean')).reset_index()
    missing_compare.to_csv(OUT/'missingness_descriptive.csv',index=False)
    tables={'Summary':sm,'Firms':ff,'Deals':deals,'Providers':lenders,'Public checks':web,'Missingness':missing_compare}
    payload={n:{'columns':list(t.columns),'rows':json.loads(t.to_json(orient='values',date_format='iso',force_ascii=False))} for n,t in tables.items()}
    (OUT/'workbook_data.json').write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8')
    manifest={'source':str(SOURCE),'sample':str(SAMPLE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'sample_sha256':hashlib.sha256(SAMPLE.read_bytes()).hexdigest(),'matched_firms':2820,'matching':'exact OrganizationName = Organization Name; one sample record to many transactions','run_date':'2026-10-15','raw_files_modified':False}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(sm.to_string(index=False)); print('\nMissingness comparison\n',missing_compare.to_string(index=False))
    print('First year mismatches:',ff.loc[ff.year_mismatch.eq(1),['OrganizationName','VDyear']].to_string(index=False))
