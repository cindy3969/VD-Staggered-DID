import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root='C:/Users/user/Documents/VD/outputs/vd_lender_validation_2820';
const data=JSON.parse(await fs.readFile(`${root}/workbook_data.json`,'utf8'));
const wb=Workbook.create();
function col(n){let s='';while(n){n--;s=String.fromCharCode(65+n%26)+s;n=Math.floor(n/26);}return s;}
const methods=[
['Topic','Definition / interpretation'],
['Population','Exact-name join of all 2,820 firms in table3_current_2820_cross_section_v2.dta. Original VD and VDyear preserved. 1,410 treated and 1,410 controls.'],
['Candidate deals','Debt=1 OR Funding Type=Debt Financing in the requested merged_v4 source. 1,898 rows. Includes two source conflicts to avoid silently dropping treated firms. Convertible Note and Post-IPO Debt are not added to the original treatment definition.'],
['Code 0','Investor names absent. This is a missingness code, not a non-VD classification. For controls, zero candidate records must be distinguished from anonymous debt.'],
['Code 1','Specialized venture/growth-debt providers, including life-sciences venture lenders. Presence supports the measure but does not establish the specific contract type.'],
['Code 2','Banks with documented venture/startup lending operations. Classification is at provider level; historical product and geographic fit are not independently established for every transaction.'],
['Code 3','Other identifiable institutional lenders/financing providers: banks, private credit, revenue-based and asset-based providers. Does not validate conventional VD.'],
['Code 4','Ambiguous: unverified lender role, equity/angel/accelerator participant, adviser, public-program exclusion review, or source funding-type conflict. Unreviewed identities remain explicit.'],
['Hierarchy','A mixed deal is assigned 1 before 2 before 3 before 4. has_cat1...has_cat4 retain overlaps. Firm category uses the same priority across candidate deals. Never sum overlapping flags as mutually exclusive groups.'],
['First versus any','first_vd_source uses First VD=1 in the source. Named first-deal firms: 715; anonymous first deals: 695. Any-deal named firms: 779; anonymous-only firms: 631. Raw missingness counts are retained after supplemental web checks.'],
['strict_lender_support','Debt Financing label AND category 1/2 AND no public-program flag AND not on/after reported IPO. It is provider corroboration, not legal contract verification. At firm level it means at least one qualifying deal.'],
['first_lender_support','Same rule restricted to the source first-VD deal. Prefer this to an any-deal flag when validating treatment onset.'],
['strict_context_support / first_context_support','Lender support plus a strictly earlier Series A-or-later round in the same source. A Series label is a VC-context proxy, not proof of institutional sponsorship.'],
['Anonymous evidence','Every anonymous record retains funding type, date, amount, prior Series rounds, prior seed/angel rounds, same-day/later Series rounds and source row. Internal indicators are correlated source evidence, not independent confirmation.'],
['Timing','Prior means strictly before Announced Date. Same-day rounds are separate. Future Series rounds and lenders in other deals do not prove the focal anonymous deal is VD.'],
['Amounts','Positive disclosed amounts provide transaction detail, not debt-contract proof. Facility commitments and funded proceeds are not assumed equivalent.'],
['Public checks','Eight purposive checks: five large anonymous transactions, two smaller anonymous transactions and one government-name exception. Not a random sample; no prevalence or false-positive rate can be inferred.'],
['External flags','external_noncore_review identifies six public checks indicating corporate/bond/government financing. Original categories and treatment are retained. external_debt_form records the finding.'],
['Government exclusion','The user reports PPP/government-backed exclusion. Source still has public-program identities. government_review is a review flag, not a claim that all such deals are guaranteed loans or PPP.'],
['Conflicts','Dermira and Eargo: Debt=1 but Series B/C; source first-debt years 2013/2017 differ from current VDyear=2015. Keep current sample and flag; do not silently repair treatment.'],
['Source columns','Investor names is Excel CB (column 80), source headers row 2; data row provenance is source_excel_row. Cumulative Investors and Top 5 Investors are not substituted for deal lenders.'],
['Identity parsing','Split comma-delimited names while retaining legal suffixes such as LLC and LP. Original text is preserved. No fuzzy corporate-name matches used.'],
['Provider review','public_source_reviewed means a source was reviewed for provider identity, not each contract. source_identity_classification means recognizable bank identity in the source only. unresolved_not_individually_web_verified means no external resolution; code 4.'],
['Missingness','Descriptive comparisons show differences between named and anonymous-only firms. Do not assume missing at random or extrapolate the named subset validation rate to all treated firms.'],
['Sensitivity use','Keep the broad original measure and report first-lender-supported and first-lender-plus-prior-Series definitions as sensitivity flags. Unknown is not zero treatment. Restricting treated firms changes matching/balance and requires a new matched-sample analysis.'],
['Source files','Requested 2010 2015 Crunchbase deals merged_v4.xlsx and current table3_current_2820_cross_section_v2.dta. Exact paths and SHA-256 hashes are in manifest.json.'],
['Research date','2026-10-15. Current/historical provider pages are cited in Providers; supplemental transaction sources in Public checks.'],
];
data.Methods={columns:methods[0],rows:methods.slice(1)};
for(const [name,t] of Object.entries(data)){
 const s=wb.worksheets.add(name); s.showGridLines=false;
 const offset=name==='Summary'?3:0;
 const datecols=t.columns.map((c,i)=>['deal_date','source_deal_date'].includes(c)?i:-1).filter(i=>i>=0);
 const rows=t.rows.map(r=>r.map((v,c)=>datecols.includes(c)&&v?new Date(v):v));
 const vals=[t.columns,...rows];
 s.getRangeByIndexes(offset,0,vals.length,t.columns.length).values=vals;
 const used=s.getUsedRange(); used.format.font={name:'Arial',size:10}; used.format.verticalAlignment='center';
 const widths=t.columns.map(c=>/finding|basis|Definition/.test(c)?80:/url|evidence|participant_categories|participants/.test(c)?65:/OrganizationName|participant_name|metric|section|anonymous_evidence|validation_group|debt_form|subtype|review_status/.test(c)?36:/Investor names|Lead Investors/.test(c)?65:18);
 for(let c=0;c<t.columns.length;c++)s.getRangeByIndexes(offset,c,vals.length,1).format.columnWidth=widths[c];
 used.format.wrapText=true; used.format.rowHeight=name==='Methods'?52:32;
 s.getRangeByIndexes(offset,0,1,t.columns.length).format={fill:'#263D57',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:54,horizontalAlignment:'center'};
 for(let r=0;r<t.rows.length;r++){
   const lines=Math.max(...t.rows[r].map((v,c)=>typeof v==='string'?Math.ceil(v.length/Math.max(10,widths[c]-4)):1));
   if(lines>2)s.getRangeByIndexes(offset+r+1,0,1,t.columns.length).format.rowHeight=lines*15+12;
 }
 for(const c of datecols)s.getRangeByIndexes(offset+1,c,t.rows.length,1).setNumberFormat('yyyy-mm-dd');
 for(let c=0;c<t.columns.length;c++){
   if(/usd$|MoneyRaised_VD|Money Raised Currency/.test(t.columns[c]))s.getRangeByIndexes(offset+1,c,t.rows.length,1).setNumberFormat('#,##0');
   if(t.columns[c]==='early_stage_share')s.getRangeByIndexes(offset+1,c,t.rows.length,1).setNumberFormat('0.0%');
 }
 s.freezePanes.freezeRows(offset+1);
 if(name!=='Methods'&&name!=='Summary')s.tables.add(`A${offset+1}:${col(t.columns.length)}${offset+vals.length}`,true,name.replace(/ /g,'')+'Table');
 if(name==='Summary'){
   s.getRange('A2').values=[['VD measurement validation — matched 2,820 firms']];
   s.getRange('A2:E2').format.font={name:'Arial',size:14,bold:true};
   s.getRange('A2').format.wrapText=false;
   s.getRange('A4:A60').format.columnWidth=32; s.getRange('B4:B60').format.columnWidth=61;
   s.getRange(`C5:D${offset+vals.length}`).setNumberFormat('#,##0');
   s.getRange(`E5:E${offset+vals.length}`).formulas=t.rows.map((r,i)=>[r[3]?`=C${i+5}/D${i+5}`:'']);
   s.getRange(`E5:E${offset+vals.length}`).setNumberFormat('0.0%');
   s.tabColor='#263D57';
 }
 if(name==='Deals')s.getRangeByIndexes(1,t.columns.indexOf('Money Raised Currency (in USD)'),t.rows.length,1).setNumberFormat('#,##0');
 console.log(name,t.rows.length);
}
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'Summary!A4:E12',include:'values,formulas',tableMaxRows:9,tableMaxCols:5})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!',options:{useRegex:true,maxResults:20}})).ndjson);
for(const name of Object.keys(data)){
 const range=name==='Summary'?'A2:E14':name==='Methods'?'A1:B6':name==='Providers'?'A1:F5':name==='Public checks'?'A1:F4':name==='Missingness'?'A1:G3':'A1:H5';
 const p=await wb.render({sheetName:name,range,scale:1,format:'png'});
 await fs.writeFile(`${root}/preview_${name.replace(/ /g,'_')}.png`,new Uint8Array(await p.arrayBuffer()));
}
const x=await SpreadsheetFile.exportXlsx(wb);await x.save(`${root}/VD_lender_validation_2820.xlsx`);
console.log('EXPORTED');
