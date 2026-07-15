"use client";

import { useState, useTransition } from "react";
import { Dialog } from "@/components/ui/dialog";
import { deleteTransactionAction } from "@/actions/transactions";
import { fmt } from "@/lib/totals";
import type { Transaction } from "@/lib/types";
import { NativeSelect } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export function DeleteTransactionDialog({
  open,
  onOpenChange,
  transactions,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  transactions: Transaction[];
}) {
  const sorted = [...transactions].sort((a, b) => a.fecha.localeCompare(b.fecha) || a.id - b.id);
  const [selected, setSelected] = useState<number | null>(sorted[0]?.id ?? null);
  const [isPending, startTransition] = useTransition();

  if (sorted.length === 0) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange} title="Eliminar movimiento">
        <p className="text-sm text-gray-600">No hay movimientos.</p>
        <Button variant="secondary" className="mt-3 w-full" onClick={() => onOpenChange(false)}>
          Cerrar
        </Button>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange} title="Eliminar movimiento">
      <NativeSelect value={selected ?? ""} onChange={(e) => setSelected(Number(e.target.value))}>
        {sorted.map((t) => (
          <option key={t.id} value={t.id}>
            {t.fecha} | {t.descripcion.slice(0, 45)} | {fmt(t.monto)} ({t.tipo === "abono" ? "Abono" : "Cargo"})
          </option>
        ))}
      </NativeSelect>
      <p className="mt-3 text-sm text-amber-700">⚠️ Esta acción no se puede deshacer.</p>
      <div className="mt-3 grid grid-cols-2 gap-3">
        <Button variant="secondary" onClick={() => onOpenChange(false)}>
          Cancelar
        </Button>
        <Button
          variant="danger"
          disabled={isPending || selected === null}
          onClick={() =>
            startTransition(async () => {
              if (selected !== null) await deleteTransactionAction(selected);
              onOpenChange(false);
            })
          }
        >
          🗑 Eliminar
        </Button>
      </div>
    </Dialog>
  );
}
