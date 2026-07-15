import { PDFDocument, StandardFonts, rgb } from "pdf-lib";
import { fmt } from "@/lib/totals";
import type { Transaction } from "@/lib/types";
import type { Period } from "@/lib/types";

const MM = 2.83465;
const PAGE_W = 297 * MM;
const PAGE_H = 210 * MM;
const MARGIN = 8 * MM;

const HEADERS = ["Fecha", "Descripcion", "Ref", "Débito ($)", "Crédito ($)", "Concepto", "Cuenta", "Origen/Destino", "Estado"];
const WIDTHS_MM = [22, 60, 26, 24, 24, 32, 22, 34, 22];
const HEADER_FILL = rgb(44 / 255, 62 / 255, 80 / 255);
const ZEBRA_FILL = rgb(245 / 255, 245 / 255, 245 / 255);

// pdf-lib's standard fonts only support WinAnsi encoding — strip anything
// outside it (emoji, en-dashes, etc.) instead of letting drawText throw.
function winAnsiSafe(s: string): string {
  return Array.from(s)
    .map((ch) => (ch.codePointAt(0)! <= 0xff ? ch : "-"))
    .join("");
}

// Replicates app.py's _export_pdf (fpdf2): a fixed landscape table with a
// dark-blue header row and zebra-striped body, same column set/widths.
export async function exportPdf(txs: Transaction[], period: Period): Promise<Uint8Array> {
  const doc = await PDFDocument.create();
  const font = await doc.embedFont(StandardFonts.Helvetica);
  const fontBold = await doc.embedFont(StandardFonts.HelveticaBold);

  const usableWidth = PAGE_W - 2 * MARGIN;
  const widthScale = usableWidth / WIDTHS_MM.reduce((a, b) => a + b, 0);
  const colWidths = WIDTHS_MM.map((w) => w * MM * widthScale);
  const headerRowH = 7 * MM;
  const dataRowH = 6 * MM;

  let page = doc.addPage([PAGE_W, PAGE_H]);
  let y = PAGE_H - MARGIN;

  const drawTitle = () => {
    page.drawText(winAnsiSafe(`Conciliacion Bancaria - ${period.nombre}`), {
      x: MARGIN,
      y: y - 5 * MM,
      size: 12,
      font: fontBold,
    });
    y -= 10 * MM;
  };

  const drawHeaderRow = () => {
    let x = MARGIN;
    page.drawRectangle({ x: MARGIN, y: y - headerRowH, width: usableWidth, height: headerRowH, color: HEADER_FILL });
    for (const [i, h] of HEADERS.entries()) {
      page.drawText(h, { x: x + 2, y: y - headerRowH + 2, size: 8, font: fontBold, color: rgb(1, 1, 1) });
      x += colWidths[i];
    }
    y -= headerRowH;
  };

  drawTitle();
  drawHeaderRow();

  txs.forEach((t, i) => {
    if (y - dataRowH < MARGIN) {
      page = doc.addPage([PAGE_W, PAGE_H]);
      y = PAGE_H - MARGIN;
      drawHeaderRow();
    }

    const cargo = t.tipo === "cargo" ? fmt(t.monto) : "$0";
    const abono = t.tipo === "abono" ? fmt(t.monto) : "$0";
    const values = [
      t.fecha,
      t.descripcion.slice(0, 40),
      t.movimiento.slice(0, 14),
      cargo,
      abono,
      t.concepto.slice(0, 22),
      t.cuenta.slice(0, 12),
      t.origen.slice(0, 20),
      t.estado,
    ].map(winAnsiSafe);

    if (i % 2 === 0) {
      page.drawRectangle({ x: MARGIN, y: y - dataRowH, width: usableWidth, height: dataRowH, color: ZEBRA_FILL });
    }

    let x = MARGIN;
    for (const [colIdx, v] of values.entries()) {
      page.drawText(v, { x: x + 2, y: y - dataRowH + 2, size: 6, font, color: rgb(0, 0, 0) });
      x += colWidths[colIdx];
    }
    y -= dataRowH;
  });

  return doc.save();
}
