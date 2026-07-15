import { getDocumentProxy, extractTextItems } from "unpdf";
import type { StructuredTextItem } from "unpdf";
import type { ParsedTx } from "./shared";

const DATE_RE = /^(\d{4}-\d{2}-\d{2}|\d{2}\/\d{2}\/\d{4})$/;
const NUM_RE = /^-?[\d.,]+$/;

function parseAmount(tok: string): number | null {
  const cleaned = tok.replace(/\./g, "").replace(",", ".").replace(/[^0-9.-]/g, "");
  const n = parseFloat(cleaned);
  return Number.isFinite(n) ? Math.abs(n) : null;
}

function normalizeDate(s: string): string {
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s;
  const m = s.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
  if (m) return `${m[3]}-${m[2]}-${m[1]}`;
  return s;
}

// Best-effort table reconstruction from PDF.js text-item positions:
// cluster items into rows by y-proximity, then look for a date token and a
// trailing numeric token per row. There's no real table-structure detection
// here (unlike pdfplumber in the original Python app) — this is intentionally
// lossy, same "N detected / M errors, confirm before appending" UX as before.
export async function parsePdf(buffer: ArrayBuffer): Promise<{ transactions: ParsedTx[]; errors: number }> {
  const transactions: ParsedTx[] = [];
  let errors = 0;

  try {
    const pdf = await getDocumentProxy(new Uint8Array(buffer));
    const { items } = await extractTextItems(pdf);

    for (const pageItems of items) {
      const sorted = [...pageItems].sort((a, b) => b.y - a.y);
      const rows: StructuredTextItem[][] = [];
      for (const item of sorted) {
        const last = rows[rows.length - 1];
        if (last && Math.abs(last[0].y - item.y) < 3) {
          last.push(item);
        } else {
          rows.push([item]);
        }
      }

      for (const row of rows) {
        row.sort((a, b) => a.x - b.x);
        const tokens = row.map((r) => r.str.trim()).filter(Boolean);
        if (tokens.length < 2) continue;

        const fecha = tokens.find((t) => DATE_RE.test(t));
        if (!fecha) continue; // not a data row (header/footer/etc.)

        let monto: number | null = null;
        for (let i = tokens.length - 1; i >= 0; i--) {
          if (tokens[i] === fecha || !NUM_RE.test(tokens[i]) || !/\d/.test(tokens[i])) continue;
          const parsed = parseAmount(tokens[i]);
          if (parsed !== null && parsed > 0) {
            monto = parsed;
            break;
          }
        }
        if (monto === null) {
          errors++;
          continue;
        }

        const descripcion = tokens.filter((t) => t !== fecha && parseAmount(t) !== monto).join(" ").slice(0, 200);
        if (!descripcion) {
          errors++;
          continue;
        }

        transactions.push({
          fecha: normalizeDate(fecha),
          descripcion,
          movimiento: "",
          tipo: "cargo",
          monto,
          concepto: "",
          cuenta: "",
          cuentaRef: "",
          origen: "",
          nota: "",
          estado: "Pendiente",
        });
      }
    }
  } catch {
    errors++;
  }

  return { transactions, errors };
}
