import { fmt, totals } from "@/lib/totals";
import type { Transaction } from "@/lib/types";

export function TotalsFooterBar({
  saldoInicial,
  transactions,
  visibleCount,
}: {
  saldoInicial: number;
  transactions: Transaction[];
  visibleCount: number;
}) {
  const conciliados = transactions.filter((t) => t.estado === "Conciliado");
  const pendientes = transactions.filter((t) => t.estado === "Pendiente");
  const { cargo, abono } = totals(conciliados);
  const credito = saldoInicial + abono;
  const dif = Math.round(credito - cargo);
  const balanced = dif === 0;

  return (
    <div className="mt-0.5 flex flex-wrap items-center gap-8 rounded-b-lg bg-[#2c3e50] px-3.5 py-2 text-sm font-bold text-white">
      <span>
        TOTAL CONCILIADOS ({conciliados.length} de {visibleCount} mov.)
      </span>
      <span>
        Débito: <span className="text-red-300">{fmt(cargo)}</span>
      </span>
      <span>
        Crédito: <span className="text-green-300">{fmt(credito)}</span>{" "}
        <span className="text-[0.68rem] opacity-70">(incl. saldo inicial)</span>
      </span>
      <span>
        Diferencia:{" "}
        <strong className={balanced ? "text-green-400" : "text-red-400"}>
          {balanced ? "CONCILIADO ✓" : `${fmt(Math.abs(dif))} ${dif >= 0 ? "▲" : "▼"}`}
        </strong>
      </span>
      <span className="text-[0.68rem] opacity-70">{pendientes.length} pendientes sin contar</span>
    </div>
  );
}
