import type { Transaction } from "@/lib/types";

const HEADERS = [
  "Fecha",
  "Descripcion",
  "N Movimiento",
  "Débito",
  "Crédito",
  "Concepto Alegra",
  "Cuenta Contable",
  "Ref Cuenta",
  "Origen/Destino",
  "Notas",
  "Estado",
];

function csvEscape(v: string | number): string {
  const s = String(v);
  if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

// BOM prefix matches the original app's `utf-8-sig` encoding, needed for
// accented characters to render correctly when opened in Excel.
export function exportCsv(txs: Transaction[]): string {
  const lines = [HEADERS.join(",")];
  for (const t of txs) {
    lines.push(
      [
        t.fecha,
        t.descripcion,
        t.movimiento,
        t.tipo === "cargo" ? t.monto : 0,
        t.tipo === "abono" ? t.monto : 0,
        t.concepto,
        t.cuenta,
        t.cuentaRef,
        t.origen,
        t.nota,
        t.estado,
      ]
        .map(csvEscape)
        .join(","),
    );
  }
  return "﻿" + lines.join("\n");
}
