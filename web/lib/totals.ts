import type { Transaction } from "./types";

export function fmt(n: number): string {
  if (!Number.isFinite(n)) return "–";
  return `$${Math.round(n).toLocaleString("en-US")}`;
}

export function totals(txs: Transaction[]): { cargo: number; abono: number } {
  let cargo = 0;
  let abono = 0;
  for (const t of txs) {
    if (t.tipo === "cargo") cargo += t.monto;
    else abono += t.monto;
  }
  return { cargo, abono };
}

// Mirrors app.py's _metrics(): totals computed ONLY over Conciliado rows,
// pendientes are informative-only, saldo final uses ALL transactions.
export function computeMetrics(saldoInicial: number, txs: Transaction[]) {
  const conciliados = txs.filter((t) => t.estado === "Conciliado");
  const pendientes = txs.filter((t) => t.estado === "Pendiente");

  const { cargo: debitoConciliado, abono: abonoConciliado } = totals(conciliados);
  const creditoConciliado = saldoInicial + abonoConciliado;
  const diferencia = creditoConciliado - debitoConciliado;

  const { cargo: pCargo, abono: pAbono } = totals(pendientes);
  const saldoPendiente = pCargo - pAbono;

  const { cargo: cargoAll, abono: abonoAll } = totals(txs);
  const saldoFinal = saldoInicial - cargoAll + abonoAll;

  return {
    saldoInicial,
    debitoConciliado,
    creditoConciliado,
    saldoFinal,
    saldoPendiente,
    diferencia,
    countConciliados: conciliados.length,
    countPendientes: pendientes.length,
  };
}

export function puedeConciliar(saldoInicial: number, txs: Transaction[]): boolean {
  const conciliados = txs.filter((t) => t.estado === "Conciliado");
  const pendientes = txs.filter((t) => t.estado === "Pendiente");
  const { cargo, abono } = totals(conciliados);
  const dif = Math.round(saldoInicial + abono - cargo);
  return dif === 0 && pendientes.length > 0;
}
