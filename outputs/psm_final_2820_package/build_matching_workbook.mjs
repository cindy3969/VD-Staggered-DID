import fs from "node:fs/promises";
import { Workbook, SpreadsheetFile } from "@oai/artifact-tool";

const base = "C:/Users/user/Documents/VD/outputs/psm_final_2820_package/manuscript_7var_rematch";

function parseCsv(text) {
  const rows = [];
  let row = [], field = "", quoted = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (ch === '"') quoted = false;
      else field += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === ',') { row.push(field); field = ""; }
    else if (ch === '\n') { row.push(field.replace(/\r$/, "")); rows.push(row); row = []; field = ""; }
    else field += ch;
  }
  if (field.length || row.length) { row.push(field); rows.push(row); }
  return rows.filter(r => r.some(v => v !== ""));
}

function typed(rows) {
  return rows.map((r, i) => r.map(v => {
    if (i === 0 || v === "") return v;
    if (/^-?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$/.test(v)) return Number(v);
    return v;
  }));
}

async function load(name) {
  const text = await fs.readFile(`${base}/${name}`, "utf8");
  return typed(parseCsv(text.replace(/^\uFEFF/, "")));
}

const wb = Workbook.create();
const summary = wb.worksheets.add("Summary");
const pairs = wb.worksheets.add("Matched Pairs");
const firms = wb.worksheets.add("Matched Firms");
const balance = wb.worksheets.add("Balance Diagnostics");

const summaryData = await load("common_support_and_summary.csv");
const pairData = await load("matched_pairs_1410.csv");
const firmData = await load("matched_firms_2820.csv");
const balanceData = await load("balance_diagnostics.csv");

summary.getRange("A2:B2").merge();
summary.getRange("A2").values = [["PSM rematch summary"]];
summary.getRange("A4:B4").values = [["Statistic", "Value"]];
summary.getRangeByIndexes(4, 0, summaryData.length - 1, 2).values = summaryData.slice(1);
summary.getRange("D4:D8").values = [["Specification"], ["1:1 nearest-neighbor logit PSM"], ["Without replacement"], ["Empirical common support"], ["Seven manuscript covariates"]];
summary.getRange("D10:D13").values = [["Interpretation"], ["Balance is evaluated with SMDs."], ["The Love plot is saved beside this workbook."], ["Matching addresses observed covariates only."]];

pairs.getRangeByIndexes(0, 0, pairData.length, pairData[0].length).values = pairData;
firms.getRangeByIndexes(0, 0, firmData.length, firmData[0].length).values = firmData;
balance.getRangeByIndexes(0, 0, balanceData.length, balanceData[0].length).values = balanceData;

for (const sheet of [summary, pairs, firms, balance]) {
  sheet.showGridLines = false;
  const used = sheet.getUsedRange();
  used.format.font = { name: "Arial", size: 10, color: "#222222" };
  used.format.verticalAlignment = "center";
}

summary.getRange("A2:B2").format.font = { name: "Arial", size: 15, bold: true, color: "#1F2937" };
summary.getRange("A4:B4").format = { fill: "#1F4E78", font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" } };
summary.getRange("A4:B21").format.borders = { preset: "all", style: "thin", color: "#D9E2F3" };
summary.getRange("A1:A21").format.columnWidth = 48;
summary.getRange("B1:B21").format.columnWidth = 18;
summary.getRange("D1:D13").format.columnWidth = 42;
summary.getRange("B5:B21").format.numberFormat = "0.000";

for (const [sheet, data] of [[pairs, pairData], [firms, firmData], [balance, balanceData]]) {
  const header = sheet.getRangeByIndexes(0, 0, 1, data[0].length);
  header.format = { fill: "#1F4E78", font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" }, wrapText: true };
  header.format.rowHeight = 36;
  sheet.freezePanes.freezeRows(1);
  sheet.getUsedRange().format.borders = { preset: "all", style: "thin", color: "#E5E7EB" };
}
pairs.getUsedRange().format.columnWidth = 16;
pairs.getRange(`B1:B${pairData.length}`).format.columnWidth = 28;
pairs.getRange(`N1:N${pairData.length}`).format.columnWidth = 28;
firms.getUsedRange().format.columnWidth = 16;
firms.getRange(`C1:C${firmData.length}`).format.columnWidth = 30;
firms.getRange(`D1:D${firmData.length}`).format.columnWidth = 42;
balance.getUsedRange().format.columnWidth = 17;
balance.getRange(`A1:A${balanceData.length}`).format.columnWidth = 42;

wb.recalculate();
const check = await wb.inspect({ kind: "table", range: "Summary!A2:D13", include: "values,formulas", tableMaxRows: 20, tableMaxCols: 6 });
console.log(check.ndjson);
const errors = await wb.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!", options: { useRegex: true, maxResults: 50 }, summary: "formula error scan" });
console.log(errors.ndjson);
const preview = await wb.render({ sheetName: "Summary", range: "A1:D21", scale: 1.5, format: "png" });
await fs.writeFile(`${base}/matching_report_preview.png`, new Uint8Array(await preview.arrayBuffer()));
const out = await SpreadsheetFile.exportXlsx(wb);
await out.save(`${base}/PSM_7var_matched_firms_and_diagnostics.xlsx`);
