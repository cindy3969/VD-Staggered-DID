import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const input = "C:/Users/user/Documents/VD/outputs/patent_application_list_rebuilt_2024/patent_application_list_through_2024.csv";
const output = "C:/Users/user/Documents/VD/outputs/patent_application_list_rebuilt_2024/full_cohort_patent_application_list_through_2024.xlsx";
const previewDir = "C:/Users/user/Documents/VD/outputs/patent_application_list_rebuilt_2024/previews";
const csvText = await fs.readFile(input, "utf8");
const workbook = await Workbook.fromCSV(csvText, { sheetName: "Applications" });
const apps = workbook.worksheets.getItem("Applications");
const summary = workbook.worksheets.add("Summary");
const sources = workbook.worksheets.add("Sources and Method");
const font = "Arial";
const headerFill = "#1F4E78";
const accent = "#D9EAF7";

// Convert analysis fields to numeric types while preserving all identifiers as text.
const numericCols = [0, 12, 21, 23, 25];
const rows = apps.getUsedRange().values;
for (let r = 1; r < rows.length; r++) {
  for (const c of numericCols) {
    if (rows[r][c] !== "" && rows[r][c] !== null) rows[r][c] = Number(rows[r][c]);
  }
}
apps.getRangeByIndexes(0, 0, rows.length, rows[0].length).values = rows;

apps.showGridLines = false;
apps.freezePanes.freezeRows(1);
apps.freezePanes.freezeColumns(2);
apps.getUsedRange().format.font = { name: font, size: 9 };
apps.getRange("A1:AB1").format = {
  fill: headerFill,
  font: { name: font, size: 9, bold: true, color: "#FFFFFF" },
  horizontalAlignment: "center",
  verticalAlignment: "center",
  wrapText: true,
  borders: { preset: "inside", style: "thin", color: "#FFFFFF" },
};
apps.getRange("A1:AB10728").format.verticalAlignment = "center";
apps.getRange("D2:D10728").format.numberFormat = "yyyy-mm-dd";
apps.getRange("K2:L10728").format.numberFormat = "yyyy-mm-dd";
apps.getRange("R2:S10728").format.numberFormat = "yyyy-mm-dd";
apps.getRange("A2:A10728").format.numberFormat = "0";
apps.getRange("M2:M10728").format.numberFormat = "0";
apps.getRange("V2:V10728").format.numberFormat = "0";
apps.getRange("X2:X10728").format.numberFormat = "0";
apps.getRange("Z2:Z10728").format.numberFormat = "0";
apps.getRange("A:A").format.columnWidth = 11;
apps.getRange("B:B").format.columnWidth = 24;
apps.getRange("C:C").format.columnWidth = 15;
apps.getRange("D:D").format.columnWidth = 13;
apps.getRange("E:G").format.columnWidth = 12;
apps.getRange("H:H").format.columnWidth = 46;
apps.getRange("I:J").format.columnWidth = 18;
apps.getRange("K:M").format.columnWidth = 14;
apps.getRange("N:N").format.columnWidth = 32;
apps.getRange("O:Q").format.columnWidth = 20;
apps.getRange("R:T").format.columnWidth = 14;
apps.getRange("U:U").format.columnWidth = 42;
apps.getRange("V:Z").format.columnWidth = 18;
apps.getRange("AA:AA").format.columnWidth = 17;
apps.getRange("AB:AB").format.columnWidth = 36;
apps.tables.add("A1:AB10728", true, "PatentApplicationsTable").style = "TableStyleMedium2";
apps.tabColor = "#5B9BD5";

summary.showGridLines = false;
summary.getRange("A2:D2").merge();
summary.getRange("A2").values = [["Full-cohort patent application list through 2024"]];
summary.getRange("A2:D2").format = { font: { name: font, size: 15, bold: true, color: "#1F1F1F" } };
summary.getRange("A4:B9").values = [
  ["Metric", "Value"],
  ["Unique applications", 10727],
  ["Ultimately granted", 6319],
  ["Not granted by snapshot", 4408],
  ["Firms with linked applications", 1149],
  ["Duplicate application IDs", 0],
];
summary.getRange("A4:B4").format = { fill: headerFill, font: { name: font, bold: true, color: "#FFFFFF" }, horizontalAlignment: "center" };
summary.getRange("A5:B9").format.font = { name: font, size: 10 };
summary.getRange("B5:B9").format.numberFormat = "#,##0";
summary.getRange("A11:D15").values = [
  ["Definition", "Value", "Check", "Status"],
  ["Counting unit", "Unique application_id", "10,727 rows", "PASS"],
  ["Granted indicator", "1 if linked to retained grant record by 2024-12-31; otherwise 0", "6,319 ones", "PASS"],
  ["Annual assignment basis", "USPTO filing_date / filing_year", "No duplicate application IDs", "PASS"],
  ["Snapshot", "2024-12-31", "Granted + not granted = total", "PASS"],
];
summary.getRange("A11:D11").format = { fill: headerFill, font: { name: font, bold: true, color: "#FFFFFF" }, horizontalAlignment: "center" };
summary.getRange("A12:D15").format.font = { name: font, size: 10 };
summary.getRange("D12:D15").format = { fill: "#E2F0D9", font: { name: font, bold: true, color: "#006100" }, horizontalAlignment: "center" };
summary.getRange("A4:B9").format.borders = { preset: "outside", style: "thin", color: "#A6A6A6" };
summary.getRange("A11:D15").format.borders = { preset: "outside", style: "thin", color: "#A6A6A6" };
summary.getRange("A:A").format.columnWidth = 30;
summary.getRange("B:B").format.columnWidth = 70;
summary.getRange("C:C").format.columnWidth = 32;
summary.getRange("D:D").format.columnWidth = 14;
summary.tabColor = "#1F4E78";

sources.showGridLines = false;
sources.getRange("A2:C2").merge();
sources.getRange("A2").values = [["Sources and reconstruction method"]];
sources.getRange("A2:C2").format.font = { name: font, size: 15, bold: true };
sources.getRange("A4:C12").values = [
  ["Item", "Specification", "Source"],
  ["USPTO data snapshot", "PatentsView metadata through 2024-12-31", "https://zenodo.org/records/15783125"],
  ["Published applications", "pg_published_application.tsv.zip", "USPTO PatentsView"],
  ["Assignee linkage", "Disambiguated and raw assignee tables; normalized firm names", "USPTO PatentsView"],
  ["Grant linkage", "Publication-to-grant crosswalk plus grant metadata", "USPTO PatentsView"],
  ["Application count", "One row per unique application_id", "10,727"],
  ["Ultimately granted", "Canonical current links plus retained historical grant-union records", "6,319"],
  ["Indicator", "ultimately_granted is numeric 1/0", "Applications!X:X"],
  ["Date basis", "Filing, publication, and grant dates are shown separately", "ISO date format"],
];
sources.getRange("A4:C4").format = { fill: headerFill, font: { name: font, bold: true, color: "#FFFFFF" }, horizontalAlignment: "center" };
sources.getRange("A5:C12").format.font = { name: font, size: 10 };
sources.getRange("A5:C12").format.wrapText = true;
sources.getRange("A:A").format.columnWidth = 25;
sources.getRange("B:B").format.columnWidth = 70;
sources.getRange("C:C").format.columnWidth = 45;
sources.getRange("A4:C12").format.borders = { preset: "outside", style: "thin", color: "#A6A6A6" };
sources.tabColor = "#A5A5A5";

workbook.recalculate();
await fs.mkdir(previewDir, { recursive: true });
for (const name of ["Summary", "Sources and Method"]) {
  const preview = await workbook.render({ sheetName: name, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(`${previewDir}/${name.replaceAll(" ", "_")}.png`, new Uint8Array(await preview.arrayBuffer()));
}
const inspect = await workbook.inspect({ kind: "sheet,table,region", maxChars: 5000, tableMaxRows: 8, tableMaxCols: 8 });
await fs.writeFile(`${previewDir}/inspect.txt`, inspect.ndjson ?? String(inspect), "utf8");
const appInspect = await workbook.inspect({ kind: "region,computedStyle", sheetId: "Applications", range: "A1:AB20", maxChars: 5000 });
await fs.writeFile(`${previewDir}/applications_inspect.txt`, appInspect.ndjson ?? String(appInspect), "utf8");
const formulaErrors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, maxChars: 4000 });
await fs.writeFile(`${previewDir}/formula_errors.txt`, formulaErrors.ndjson ?? String(formulaErrors), "utf8");
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(output);
console.log(output);
