import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";
const input = await FileBlob.load("C:/Users/user/Documents/VD/.artifact_work/series_preview.xlsx");
const wb = await SpreadsheetFile.importXlsx(input);
const img = await wb.render({ sheetName: "Sheet1", range: "A1:N35", scale: 1, format: "png" });
await fs.writeFile("C:/Users/user/Documents/VD/.artifact_work/series_preview.png", new Uint8Array(await img.arrayBuffer()));
const check = await wb.inspect({ kind: "region", sheetId: "Sheet1", range: "A1:N35", maxChars: 4000 });
console.log(check.ndjson);
