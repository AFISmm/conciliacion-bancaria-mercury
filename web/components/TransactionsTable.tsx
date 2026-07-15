"use client";

import { useTransition } from "react";
import { updateTransactionFieldAction, type EditableInlineField } from "@/actions/transactions";
import { fmt } from "@/lib/totals";
import { ESTADOS } from "@/lib/companies";
import type { Transaction } from "@/lib/types";

const EDITABLE_COLUMNS: { key: EditableInlineField; label: string; width: string; type: "text" | "select" }[] = [
  { key: "concepto", label: "Concepto Alegra", width: "130px", type: "text" },
  { key: "cuenta", label: "Cta. Contable", width: "100px", type: "text" },
  { key: "cuentaRef", label: "Ref. Cuenta", width: "120px", type: "text" },
  { key: "origen", label: "Origen/Destino", width: "120px", type: "text" },
  { key: "nota", label: "Notas", width: "120px", type: "text" },
  { key: "estado", label: "Estado", width: "130px", type: "select" },
];

const cellClass =
  "w-full rounded border border-transparent bg-transparent px-1 py-0.5 hover:border-gray-300 focus:border-[#2c3e50] focus:outline-none";

export function TransactionsTable({ transactions }: { transactions: Transaction[] }) {
  const [, startTransition] = useTransition();

  if (transactions.length === 0) {
    return <p className="rounded-md bg-blue-50 px-3 py-2 text-sm text-blue-700">Sin movimientos en este filtro.</p>;
  }

  function commit(txId: number, field: EditableInlineField, value: string) {
    startTransition(() => {
      updateTransactionFieldAction(txId, field, value);
    });
  }

  return (
    <div className="overflow-x-auto rounded-t-lg border border-gray-200">
      <table className="w-full min-w-[1100px] text-xs">
        <thead className="bg-gray-100 text-gray-600">
          <tr>
            <th className="px-2 py-1.5 text-left">Fecha</th>
            <th className="px-2 py-1.5 text-left">Descripción</th>
            <th className="px-2 py-1.5 text-left">N° Mov.</th>
            <th className="px-2 py-1.5 text-right">Débito ($)</th>
            <th className="px-2 py-1.5 text-right">Crédito ($)</th>
            {EDITABLE_COLUMNS.map((c) => (
              <th key={c.key} className="px-2 py-1.5 text-left" style={{ minWidth: c.width }}>
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {transactions.map((t) => (
            <tr key={t.id} className="border-t border-gray-100 hover:bg-gray-50">
              <td className="whitespace-nowrap px-2 py-1 text-gray-700">{t.fecha}</td>
              <td className="px-2 py-1 text-gray-700">{t.descripcion}</td>
              <td className="whitespace-nowrap px-2 py-1 text-gray-700">{t.movimiento}</td>
              <td className="whitespace-nowrap px-2 py-1 text-right text-red-600">
                {t.tipo === "cargo" ? fmt(t.monto) : ""}
              </td>
              <td className="whitespace-nowrap px-2 py-1 text-right text-green-700">
                {t.tipo === "abono" ? fmt(t.monto) : ""}
              </td>
              {EDITABLE_COLUMNS.map((c) => (
                <td key={c.key} className="px-1 py-0.5">
                  {c.type === "select" ? (
                    <select
                      defaultValue={t[c.key]}
                      onChange={(e) => commit(t.id, c.key, e.target.value)}
                      className={cellClass}
                    >
                      {ESTADOS.map((s) => (
                        <option key={s} value={s}>
                          {s}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      defaultValue={t[c.key]}
                      onBlur={(e) => {
                        if (e.target.value !== t[c.key]) commit(t.id, c.key, e.target.value);
                      }}
                      className={cellClass}
                    />
                  )}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
