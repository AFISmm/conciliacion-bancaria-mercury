"use client";

import { fmt, totals } from "@/lib/totals";
import { filterTransactions, type FilterState } from "@/lib/filters";
import type { Transaction } from "@/lib/types";
import { NativeSelect } from "@/components/ui/input";

const MODE_LABELS: Record<FilterState["mode"], string> = {
  month: "Mes completo",
  day: "Día",
  week: "Semana",
  biweek: "Quincena",
};

export function PeriodFilters({
  filter,
  onChange,
  transactions,
}: {
  filter: FilterState;
  onChange: (filter: FilterState) => void;
  transactions: Transaction[];
}) {
  const filtered = filterTransactions(transactions, filter);
  const { cargo, abono } = totals(filtered);
  const months = Array.from(new Set(transactions.map((t) => t.fecha.slice(0, 7)))).sort();

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      <div>
        <p className="mb-1 text-xs font-semibold text-gray-600">Vista</p>
        <div className="flex flex-wrap gap-1">
          {(Object.keys(MODE_LABELS) as FilterState["mode"][]).map((mode) => (
            <button
              key={mode}
              onClick={() => onChange({ ...filter, mode })}
              className={`rounded-full px-3 py-1 text-xs font-medium ${
                filter.mode === mode ? "bg-[#2c3e50] text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {MODE_LABELS[mode]}
            </button>
          ))}
        </div>
      </div>

      <div>
        {filter.mode === "day" && (
          <>
            <p className="mb-1 text-xs font-semibold text-gray-600">Fecha</p>
            <input
              type="date"
              className="w-full rounded-md border border-gray-300 px-2.5 py-1.5 text-sm"
              value={filter.date ?? ""}
              onChange={(e) => onChange({ ...filter, date: e.target.value })}
            />
          </>
        )}
        {filter.mode === "week" && (
          <>
            <p className="mb-1 text-xs font-semibold text-gray-600">Fecha en semana</p>
            <input
              type="date"
              className="w-full rounded-md border border-gray-300 px-2.5 py-1.5 text-sm"
              value={filter.date ?? ""}
              onChange={(e) => onChange({ ...filter, date: e.target.value })}
            />
          </>
        )}
        {filter.mode === "biweek" && (
          <div className="flex gap-2">
            <div className="flex-1">
              <p className="mb-1 text-xs font-semibold text-gray-600">Mes</p>
              <NativeSelect value={filter.bwMonth ?? ""} onChange={(e) => onChange({ ...filter, bwMonth: e.target.value })}>
                {months.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </NativeSelect>
            </div>
            <div className="flex-1">
              <p className="mb-1 text-xs font-semibold text-gray-600">Quincena</p>
              <NativeSelect
                value={String(filter.bwHalf ?? 1)}
                onChange={(e) => onChange({ ...filter, bwHalf: Number(e.target.value) as 1 | 2 })}
              >
                <option value="1">1ª (1–15)</option>
                <option value="2">2ª (16–fin)</option>
              </NativeSelect>
            </div>
          </div>
        )}
      </div>

      <div className="flex items-end">
        <p className="text-xs text-gray-600">
          <strong>{filtered.length}</strong> mov. | Cargos <strong>{fmt(cargo)}</strong> | Abonos <strong>{fmt(abono)}</strong>
        </p>
      </div>
    </div>
  );
}
