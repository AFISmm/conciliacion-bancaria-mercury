import Papa from "papaparse";
import { rowsToTransactions } from "./shared";

export function parseCsv(raw: string) {
  const { data } = Papa.parse<string[]>(raw.trim(), { skipEmptyLines: true });
  return rowsToTransactions(data);
}
