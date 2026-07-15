"use client";

import { useState, useTransition } from "react";
import { importTransactionsAction } from "@/actions/transactions";
import type { ParsedTx } from "@/lib/import/shared";
import { Button } from "@/components/ui/button";

type ParseResult = { transactions: ParsedTx[]; errors: number } | { error: string };

function Uploader({
  label,
  accept,
  kind,
  companyId,
  periodId,
}: {
  label: string;
  accept: string;
  kind: "csv" | "excel" | "pdf";
  companyId: string;
  periodId: string;
}) {
  const [result, setResult] = useState<ParseResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [isPending, startTransition] = useTransition();
  const [confirmed, setConfirmed] = useState(false);

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setConfirmed(false);
    setLoading(true);
    setResult(null);
    try {
      const formData = new FormData();
      formData.set("file", file);
      formData.set("kind", kind);
      const res = await fetch("/api/import", { method: "POST", body: formData });
      const data = await res.json();
      setResult(data);
    } catch {
      setResult({ error: "Error al subir el archivo." });
    } finally {
      setLoading(false);
      e.target.value = "";
    }
  }

  const rows = result && "transactions" in result ? result.transactions : [];

  return (
    <div className="flex flex-col gap-1.5">
      <p className="text-xs font-semibold text-gray-600">{label}</p>
      <input
        type="file"
        accept={accept}
        onChange={handleFile}
        className="text-xs file:mr-2 file:rounded file:border-0 file:bg-gray-100 file:px-2 file:py-1 file:text-xs"
      />
      {loading && <p className="text-xs text-gray-500">Procesando…</p>}
      {result && "error" in result && <p className="text-xs text-red-600">{result.error}</p>}
      {result && "transactions" in result && (
        <>
          <p className="text-xs text-gray-500">
            {rows.length} detectadas{result.errors ? `, ${result.errors} errores` : ""}
          </p>
          {rows.length > 0 && !confirmed && (
            <Button
              variant="secondary"
              disabled={isPending}
              onClick={() =>
                startTransition(async () => {
                  await importTransactionsAction(companyId, periodId, rows);
                  setConfirmed(true);
                })
              }
            >
              Confirmar {rows.length} filas
            </Button>
          )}
          {confirmed && <p className="text-xs text-green-700">Importado ✓</p>}
        </>
      )}
    </div>
  );
}

export function ImportPanel({ companyId, periodId }: { companyId: string; periodId: string }) {
  return (
    <div>
      <p className="mb-2 text-sm font-semibold text-[#2c3e50]">⬆️ Importar extracto</p>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Uploader label="CSV" accept=".csv,.txt" kind="csv" companyId={companyId} periodId={periodId} />
        <Uploader label="Excel" accept=".xlsx,.xls" kind="excel" companyId={companyId} periodId={periodId} />
        <Uploader label="PDF" accept=".pdf" kind="pdf" companyId={companyId} periodId={periodId} />
      </div>
    </div>
  );
}
