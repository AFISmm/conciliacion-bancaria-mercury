"use client";

import { useMemo, useState, useTransition } from "react";
import { Sidebar } from "@/components/Sidebar";
import { MetricsRow } from "@/components/MetricsRow";
import { PeriodFilters } from "@/components/PeriodFilters";
import { TransactionsTable } from "@/components/TransactionsTable";
import { TotalsFooterBar } from "@/components/TotalsFooterBar";
import { ImportPanel } from "@/components/ImportPanel";
import { ExportPanel } from "@/components/ExportPanel";
import { AlegraPanel } from "@/components/AlegraPanel";
import { PeriodDialog } from "@/components/dialogs/PeriodDialog";
import { TransactionDialog } from "@/components/dialogs/TransactionDialog";
import { DeleteTransactionDialog } from "@/components/dialogs/DeleteTransactionDialog";
import { ConciliarDialog } from "@/components/dialogs/ConciliarDialog";
import { Button } from "@/components/ui/button";
import { computeMetrics, puedeConciliar } from "@/lib/totals";
import { filterTransactions, type FilterState } from "@/lib/filters";
import { validarAction } from "@/actions/transactions";
import type { Company, Period, Transaction } from "@/lib/types";

type Dialog = "new_period" | "edit_period" | "tx" | "eliminar_tx" | "conciliar" | null;
type Tab = "movimientos" | "periodo" | "alegra";

export function Dashboard({
  userName,
  companies,
  currentCompanyId,
  periods,
  currentPeriod,
  transactions,
  alegraEmail,
  alegraToken,
}: {
  userName: string;
  companies: Company[];
  currentCompanyId: string | null;
  periods: Period[];
  currentPeriod: Period | null;
  transactions: Transaction[];
  alegraEmail: string;
  alegraToken: string;
}) {
  const [dialog, setDialog] = useState<Dialog>(null);
  const [tab, setTab] = useState<Tab>("movimientos");
  const [filter, setFilter] = useState<FilterState>({ mode: "month" });
  const [toast, setToast] = useState<string | null>(null);
  const [isValidating, startValidating] = useTransition();

  const filtered = useMemo(() => filterTransactions(transactions, filter), [transactions, filter]);
  const metrics = useMemo(
    () => (currentPeriod ? computeMetrics(currentPeriod.saldoInicial, transactions) : null),
    [currentPeriod, transactions],
  );
  const canConciliar = currentPeriod ? puedeConciliar(currentPeriod.saldoInicial, transactions) : false;

  if (!currentCompanyId) {
    return (
      <div className="flex min-h-screen">
        <Sidebar
          userName={userName}
          companies={companies}
          currentCompanyId={currentCompanyId}
          periods={[]}
          currentPeriod={null}
          alegraEmail={alegraEmail}
          alegraToken={alegraToken}
          onNewPeriod={() => {}}
          onEditPeriod={() => {}}
        />
        <main className="flex flex-1 flex-col items-center justify-center text-center">
          <div className="mb-4 text-5xl">🏦</div>
          <h1 className="text-2xl font-extrabold tracking-wide text-[#2c3e50]">PORTAL DE CONCILIACIONES</h1>
          <p className="mt-3 max-w-sm text-sm text-gray-500">Seleccione una empresa en el panel izquierdo para comenzar</p>
        </main>
      </div>
    );
  }

  const companyName = companies.find((c) => c.id === currentCompanyId)?.name ?? "";

  return (
    <div className="flex min-h-screen">
      <Sidebar
        userName={userName}
        companies={companies}
        currentCompanyId={currentCompanyId}
        periods={periods}
        currentPeriod={currentPeriod}
        alegraEmail={alegraEmail}
        alegraToken={alegraToken}
        onNewPeriod={() => setDialog("new_period")}
        onEditPeriod={() => setDialog("edit_period")}
      />

      <main className="flex-1 p-4">
        <div className="mb-3 flex items-center justify-between rounded-lg bg-[#2c3e50] px-5 py-3 text-white">
          <strong className="text-base">🏦 Conciliación Bancaria — {companyName}</strong>
          <span className="text-xs opacity-75">
            {currentPeriod ? `${currentPeriod.nombre} | Cta: ${currentPeriod.cuenta || "–"} | ${currentPeriod.banco}` : "Sin período"}
          </span>
        </div>

        {!currentPeriod ? (
          <p className="rounded-md bg-blue-50 px-3 py-2 text-sm text-blue-700">
            Sin períodos. Use ➕ Nuevo en el panel lateral para crear el primero.
          </p>
        ) : (
          <>
            {metrics && <MetricsRow metrics={metrics} />}

            <div className="mt-4 flex gap-1 border-b border-gray-200">
              {(
                [
                  ["movimientos", "📊 Movimientos"],
                  ["periodo", "📅 Período y Filtros"],
                  ["alegra", "🔗 Alegra"],
                ] as [Tab, string][]
              ).map(([key, label]) => (
                <button
                  key={key}
                  onClick={() => setTab(key)}
                  className={`px-4 py-2 text-sm font-medium ${
                    tab === key ? "border-b-2 border-[#2c3e50] text-[#2c3e50]" : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>

            <div className="py-4">
              {tab === "movimientos" && (
                <>
                  <TransactionsTable transactions={filtered} />
                  <TotalsFooterBar saldoInicial={currentPeriod.saldoInicial} transactions={transactions} visibleCount={filtered.length} />

                  <div className="mt-3 flex flex-wrap items-center gap-2">
                    <Button
                      variant="secondary"
                      disabled={isValidating}
                      onClick={() =>
                        startValidating(async () => {
                          const res = await validarAction(currentCompanyId, currentPeriod.id);
                          setToast(
                            `Validado — Conciliados: ${res.conciliados} · Pendientes: ${res.pendientes}`,
                          );
                          setTimeout(() => setToast(null), 4000);
                        })
                      }
                    >
                      🔄 Validar movimientos
                    </Button>
                    <Button variant="primary" disabled={!canConciliar} onClick={() => setDialog("conciliar")}>
                      {canConciliar ? "✅ Conciliar período" : "✅ Conciliar (diferencia ≠ 0)"}
                    </Button>
                    <Button variant="secondary" onClick={() => setDialog("tx")}>
                      ＋ Agregar movimiento
                    </Button>
                    <Button variant="secondary" onClick={() => setDialog("eliminar_tx")}>
                      🗑 Eliminar movimiento
                    </Button>
                    {toast && <span className="text-xs font-medium text-green-700">✅ {toast}</span>}
                  </div>

                  <hr className="my-4 border-gray-200" />

                  <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                    <ImportPanel companyId={currentCompanyId} periodId={currentPeriod.id} />
                    <ExportPanel companyId={currentCompanyId} periodId={currentPeriod.id} filter={filter} />
                  </div>
                </>
              )}

              {tab === "periodo" && (
                <PeriodFilters filter={filter} onChange={setFilter} transactions={transactions} />
              )}

              {tab === "alegra" && <AlegraPanel email={alegraEmail} token={alegraToken} />}
            </div>
          </>
        )}
      </main>

      {(dialog === "new_period" || dialog === "edit_period") && (
        <PeriodDialog
          open
          onOpenChange={(v) => !v && setDialog(null)}
          companyId={currentCompanyId}
          period={dialog === "edit_period" ? currentPeriod : null}
        />
      )}
      {dialog === "tx" && currentPeriod && (
        <TransactionDialog
          open
          onOpenChange={(v) => !v && setDialog(null)}
          companyId={currentCompanyId}
          periodId={currentPeriod.id}
        />
      )}
      {dialog === "eliminar_tx" && (
        <DeleteTransactionDialog open onOpenChange={(v) => !v && setDialog(null)} transactions={transactions} />
      )}
      {dialog === "conciliar" && currentPeriod && (
        <ConciliarDialog
          open
          onOpenChange={(v) => !v && setDialog(null)}
          companyId={currentCompanyId}
          periodId={currentPeriod.id}
          saldoInicial={currentPeriod.saldoInicial}
          transactions={transactions}
        />
      )}
    </div>
  );
}
