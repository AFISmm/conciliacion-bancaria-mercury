import { fmt } from "@/lib/totals";
import type { computeMetrics } from "@/lib/totals";

type Metrics = ReturnType<typeof computeMetrics>;

function Tile({ label, value, delta }: { label: string; value: string; delta?: string }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white px-3.5 py-2.5 shadow-sm">
      <div className="text-[0.72rem] text-gray-500">{label}</div>
      <div className="text-base font-bold text-[#2c3e50]">{value}</div>
      {delta && <div className="mt-0.5 text-[0.68rem] text-gray-400">{delta}</div>}
    </div>
  );
}

export function MetricsRow({ metrics }: { metrics: Metrics }) {
  const {
    saldoInicial,
    debitoConciliado,
    creditoConciliado,
    saldoFinal,
    saldoPendiente,
    diferencia,
    countConciliados,
    countPendientes,
  } = metrics;

  const difBalanced = Math.round(diferencia) === 0;

  return (
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-4 lg:grid-cols-8">
      <Tile label="Saldo Inicial" value={fmt(saldoInicial)} />
      <Tile label="Débito Conciliado" value={fmt(debitoConciliado)} delta={`${countConciliados} movimientos`} />
      <Tile label="Crédito Conciliado" value={fmt(creditoConciliado)} delta="incl. saldo inicial" />
      <Tile label="Saldo Final (real)" value={fmt(saldoFinal)} />
      <Tile
        label="Saldo Pend. por Conciliar"
        value={fmt(Math.abs(saldoPendiente))}
        delta={`${saldoPendiente >= 0 ? "Déb" : "Créd"} · ${countPendientes} mov.`}
      />
      <Tile
        label="Diferencia Conciliación"
        value={fmt(Math.abs(diferencia))}
        delta={difBalanced ? "Balanceado ✓" : "Por ajustar"}
      />
      <Tile label="Conciliados" value={String(countConciliados)} />
      <Tile label="Pendientes" value={String(countPendientes)} />
    </div>
  );
}
