import type { Estado, Tipo } from "@/lib/companies";

export type ParsedTx = {
  fecha: string;
  descripcion: string;
  movimiento: string;
  tipo: Tipo;
  monto: number;
  concepto: string;
  cuenta: string;
  cuentaRef: string;
  origen: string;
  nota: string;
  estado: Estado;
};

// Positional column mapping shared by CSV/Excel import, mirroring the
// original app._parse_csv column order: fecha, desc, mov, tipo, monto,
// concepto, cuenta, cuentaRef, origen, nota, estado.
export function rowsToTransactions(rows: string[][]): { transactions: ParsedTx[]; errors: number } {
  const transactions: ParsedTx[] = [];
  let errors = 0;

  for (const r of rows) {
    try {
      const fecha = (r[0] ?? "").trim();
      const desc = (r[1] ?? "").trim();
      if (!fecha || !desc) {
        errors++;
        continue;
      }
      const monto = parseFloat((r[4] ?? "0").replace(",", "."));
      if (!(monto > 0)) {
        errors++;
        continue;
      }
      const tipoRaw = (r[3] ?? "cargo").toLowerCase();
      const tipo: Tipo = ["cargo", "retiro", "deb"].some((x) => tipoRaw.includes(x)) ? "cargo" : "abono";
      transactions.push({
        fecha,
        descripcion: desc,
        movimiento: (r[2] ?? "").trim(),
        tipo,
        monto,
        concepto: (r[5] ?? "").trim(),
        cuenta: (r[6] ?? "").trim(),
        cuentaRef: (r[7] ?? "").trim(),
        origen: (r[8] ?? "").trim(),
        nota: (r[9] ?? "").trim(),
        estado: ((r[10] ?? "Pendiente").trim() || "Pendiente") as Estado,
      });
    } catch {
      errors++;
    }
  }

  return { transactions, errors };
}
