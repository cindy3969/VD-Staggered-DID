import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = "C:/Users/user/Documents/VD/outputs/table2_forward_citation_year_methods_39249";
const panelFullText = await fs.readFile(`${root}/firm_year_with_citations_excel_view.csv`, "utf8");
const panelText = panelFullText.split(/\r?\n/).slice(0, 501).join("\n");
const resultText = await fs.readFile(`${root}/Table2_all_truncation_methods_results.csv`, "utf8");
const qa = JSON.parse(await fs.readFile(`${root}/QA_summary.json`, "utf8"));
const workbook = await Workbook.fromCSV(panelText, { sheetName: "Panel Preview" });
const panel = workbook.worksheets.getItem("Panel Preview");
const results = workbook.worksheets.add("DiD Results");
const methods = workbook.worksheets.add("Methods and QA");
const navy = "#1F4E78", blue = "#D9EAF7", green = "#E2F0D9", font = "Arial";

panel.showGridLines = false;
panel.freezePanes.freezeRows(1);
panel.freezePanes.freezeColumns(3);
panel.getRange("A1:T1").format = { fill: navy, font: { name: font, size: 9, bold: true, color: "#FFFFFF" }, wrapText: true, horizontalAlignment: "center" };
panel.getRange("A1:A2").format.columnWidth = 12;
panel.getRange("B1:B2").format.columnWidth = 30;
panel.getRange("C1:T2").format.columnWidth = 14;

const lines = resultText.trim().split(/\r?\n/).map(line => line.split(","));
const values = lines.map((row, r) => row.map((v, c) => r === 0 || c < 2 ? v : (v === "" ? "" : Number(v))));
results.getRangeByIndexes(0, 0, values.length, values[0].length).values = values;
results.showGridLines = false;
results.freezePanes.freezeRows(1);
results.getUsedRange().format.font = { name: font, size: 10 };
results.getRangeByIndexes(0, 0, 1, values[0].length).format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" }, wrapText: true, horizontalAlignment: "center" };
results.getUsedRange().format.autofitColumns();
results.getUsedRange().format.autofitRows();
results.getRange("A:A").format.columnWidth = 25;
results.getRange("B:B").format.columnWidth = 14;

methods.showGridLines = false;
methods.getRange("A2:D2").merge();
methods.getRange("A2").values = [["Forward citation right-truncation methods and QA"]];
methods.getRange("A2:D2").format.font = { name: font, size: 15, bold: true };
const methodRows = [
  ["Variable", "Construction", "Cohort denominator", "Use"],
  ["fwd_raw", "Grant-date-or-later citation links received in calendar year, summed by firm", "None", "Unadjusted benchmark"],
  ["fwd_norm_cohort", "Application-year n_cites divided by its cohort mean; then summed by firm-year", "Filing year x citation year, including zero-citation application-years", "Requested dynamic cohort correction"],
  ["fwd_norm_cohort_cpc", "Same as fwd_norm_cohort with primary CPC3 split", "Filing year x citation year x CPC3", "Paper-inspired technology adjustment"],
  ["fwd_rate", "Cumulative citations through year divided by observed post-grant years; summed by firm-year", "Exposure time", "Annualized citation-rate correction"],
  ["fwd_rate_norm", "Annualized rate divided by cohort mean", "Filing year x citation year", "Rate plus cohort correction"],
  ["fwd_rate_norm_cpc", "Annualized rate divided by CPC cohort mean", "Filing year x citation year x CPC3", "Rate plus technology correction"],
];
methods.getRangeByIndexes(4, 0, methodRows.length, 4).values = methodRows;
methods.getRange("A5:D5").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" }, horizontalAlignment: "center" };
methods.getRange("A6:D11").format.wrapText = true;
const qaRows = [
  ["QA metric", "Value"],
  ["Input applications", qa.application_rows],
  ["Grant-linked applications", qa.grant_linked_applications],
  ["Target grant patents", qa.target_grant_patents],
  ["Valid dated post-grant citation links", qa.dated_valid_citation_links],
  ["Application-year grid rows", qa.application_year_grid_rows],
  ["CPC-covered applications", qa.cpc_covered_applications],
  ["Final panel rows", qa.panel_rows],
  ["Final panel firms", qa.panel_firms],
  ["Legacy vs rebuilt citation correlation", qa.legacy_vs_rebuilt_total_correlation],
  ["Citation cutoff year", qa.citation_cutoff_year],
];
methods.getRangeByIndexes(13, 0, qaRows.length, 2).values = qaRows;
methods.getRange("A14:B14").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" }, horizontalAlignment: "center" };
methods.getRange("B15:B23").format.fill = green;
methods.getRange("A26:C29").values = [
  ["Source", "Role", "Location"],
  ["Corrected application union", "39,721 after 737 mismatch removals; 39,249 unique firm x application_id filings in 2010-2024", "outputs/csdid_union_corrected_3yr/application_level_union_corrected_visible_mismatches.csv"],
  ["PatentsView 2024 final release", "Dated US patent citations and current CPC", "https://zenodo.org/records/15058362"],
  ["Verified Table 1 master panel", "Treatment, controls, and subgroup definitions", "outputs/csdid_historical_replication_verified/MASTER_CS_TABLE_restored.dta"],
];
methods.getRange("A26:C26").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" }, horizontalAlignment: "center" };
methods.getRange("A5:D29").format.font = { name: font, size: 10 };
methods.getRange("A:A").format.columnWidth = 30;
methods.getRange("B:B").format.columnWidth = 72;
methods.getRange("C:C").format.columnWidth = 58;
methods.getRange("D:D").format.columnWidth = 32;
methods.getRange("A5:D29").format.verticalAlignment = "center";
methods.getRange("A5:D29").format.wrapText = true;

workbook.recalculate();
await fs.mkdir(`${root}/previews`, { recursive: true });
for (const name of ["DiD Results", "Methods and QA"]) {
  const img = await workbook.render({ sheetName: name, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(`${root}/previews/${name.replaceAll(" ", "_")}.png`, new Uint8Array(await img.arrayBuffer()));
}
const inspect = await workbook.inspect({ kind: "region", sheetId: "Panel Preview", range: "A1:T12", maxChars: 7000 });
await fs.writeFile(`${root}/previews/panel_inspect.txt`, inspect.ndjson ?? String(inspect), "utf8");
const errors1 = await workbook.inspect({ kind: "match", sheetId: "DiD Results", range: `A1:J${values.length}`, searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, maxChars: 2000 });
const errors2 = await workbook.inspect({ kind: "match", sheetId: "Methods and QA", range: "A1:D29", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, maxChars: 2000 });
await fs.writeFile(`${root}/previews/formula_errors.txt`, `${errors1.ndjson ?? String(errors1)}\n${errors2.ndjson ?? String(errors2)}`, "utf8");
const file = await SpreadsheetFile.exportXlsx(workbook);
await file.save(`${root}/Table2_forward_citation_results.xlsx`);
console.log(`${root}/Table2_forward_citation_results.xlsx`);
