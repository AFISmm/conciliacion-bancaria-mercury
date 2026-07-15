"use client";

import { useState, useTransition } from "react";
import { Dialog } from "@/components/ui/dialog";
import { conciliarPeriodoAction } from "@/actions/transactions";
import { fmt, totals } from "@/lib/totals";
import type { Transaction } from "@/lib/types";
import { Button } from "@/components/ui/button";

export function ConciliarDialog({
  open,
  onOpenChange,
  companyId,
  periodId,
  saldoInicial,
  transactions,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  companyId: string;
  periodId: string;
  saldoInicial: number;
  transactions: Transaction[];
}) {
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  const conciliados = transactions.filter((t) => t.estado === "Conciliado");
  const pendientes = transactions.filter((t) => t.estado === "Pendiente");
  const { cargo, abono } = totals(conciliados);
  const credito = saldoInicial + abono;
  const dif = Math.round(credito - cargo);

  return (
    <Dialog open={open} onOpenChange={onOpenChange} title="Conciliar período" wide>
      <p className="rounded-md bg-green-50 px-3 py-2 text-sm text-green-700">
        ✅ La conciliación está balanceada — Débito = Crédito = <strong>{fmt(cargo)}</strong>
      </p>

      <div className="my-3 grid grid-cols-3 gap-3 text-center">
        <div>
          <p className="text-xs text-gray-500">Débito conciliado</p>
          <p className="font-bold text-[#2c3e50]">{fmt(cargo)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Crédito conciliado</p>
          <p className="font-bold text-[#2c3e50]">{fmt(credito)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Diferencia</p>
          <p className="font-bold text-[#2c3e50]">{dif === 0 ? "Balanceado ✓" : fmt(dif)}</p>
        </div>
      </div>

      {pendientes.length > 0 && (
        <div className="mb-3">
          <p className="text-sm text-amber-700">
            ⚠️ Quedan <strong>{pendientes.length}</strong> movimientos en estado Pendiente sin conciliar.
          </p>
          <div className="mt-2 max-h-40 overflow-y-auto rounded border border-gray-200 text-xs">
            <table className="w-full">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-2 py-1 text-left">Fecha</th>
                  <th className="px-2 py-1 text-left">Descripción</th>
                  <th className="px-2 py-1 text-right">Débito ($)</th>
                  <th className="px-2 py-1 text-right">Crédito ($)</th>
                </tr>
              </thead>
              <tbody>
                {pendientes.map((t) => (
                  <tr key={t.id} className="border-t border-gray-100">
                    <td className="px-2 py-1">{t.fecha}</td>
                    <td className="px-2 py-1">{t.descripcion.slice(0, 45)}</td>
                    <td className="px-2 py-1 text-right">{t.tipo === "cargo" ? fmt(t.monto) : "—"}</td>
                    <td className="px-2 py-1 text-right">{t.tipo === "abono" ? fmt(t.monto) : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <p className="text-sm text-gray-600">
        Al confirmar se cerrará la conciliación del período y los movimientos pendientes quedarán marcados como
        Conciliado.
      </p>

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}

      <div className="mt-3 grid grid-cols-2 gap-3">
        <Button variant="secondary" onClick={() => onOpenChange(false)}>
          Cancelar
        </Button>
        <Button
          variant="primary"
          disabled={isPending}
          onClick={() =>
            startTransition(async () => {
              const res = await conciliarPeriodoAction(companyId, periodId);
              if (res?.error) setError(res.error);
              else onOpenChange(false);
            })
          }
        >
          ✅ Confirmar y cerrar conciliación
        </Button>
      </div>
    </Dialog>
  );
}
