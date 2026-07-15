import ExcelJS from "exceljs";
import { rowsToTransactions } from "./shared";

function cellToString(v: ExcelJS.CellValue): string {
  if (v === null || v === undefined) return "";
  if (v instanceof Date) return v.toISOString().slice(0, 10);
  if (typeof v === "object") {
    if ("result" in v) return String(v.result ?? "");
    if ("text" in v) return String(v.text ?? "");
    if ("richText" in v) return v.richText.map((r) => r.text).join("");
  }
  return String(v);
}

export async function parseExcel(buffer: ArrayBuffer) {
  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.load(buffer);
  const sheet = workbook.worksheets[0];
  if (!sheet) return { transactions: [], errors: 0 };

  const rows: string[][] = [];
  sheet.eachRow((row) => {
    const values = row.values as ExcelJS.CellValue[]; // 1-indexed; index 0 is unused
    rows.push(values.slice(1).map(cellToString));
  });

  // First row is the header (matches pandas.read_excel default behavior).
  return rowsToTransactions(rows.slice(1));
}
