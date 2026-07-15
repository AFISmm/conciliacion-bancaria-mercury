"use client";

import { useActionState, useEffect, useRef } from "react";
import { Dialog } from "@/components/ui/dialog";
import { upsertTransactionAction } from "@/actions/transactions";
import { ESTADOS } from "@/lib/companies";
import { Input, Label, NativeSelect } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export function TransactionDialog({
  open,
  onOpenChange,
  companyId,
  periodId,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  companyId: string;
  periodId: string;
}) {
  const action = upsertTransactionAction.bind(null, companyId, periodId, null);
  const [state, dispatch, pending] = useActionState(action, undefined);
  const prevPending = useRef(pending);

  useEffect(() => {
    if (prevPending.current && !pending && !state?.error) onOpenChange(false);
    prevPending.current = pending;
  }, [pending, state, onOpenChange]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange} title="Agregar movimiento" wide>
      <form action={dispatch} className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label htmlFor="fecha">Fecha *</Label>
            <Input id="fecha" name="fecha" type="date" required defaultValue={new Date().toISOString().slice(0, 10)} />
          </div>
          <div>
            <Label htmlFor="tipo">Tipo *</Label>
            <NativeSelect id="tipo" name="tipo" defaultValue="cargo">
              <option value="cargo">Débito (Cargo)</option>
              <option value="abono">Crédito (Abono)</option>
            </NativeSelect>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label htmlFor="monto">Monto * ($)</Label>
            <Input id="monto" name="monto" type="number" step="0.01" min="0.01" required />
          </div>
          <div>
            <Label htmlFor="movimiento">N° Movimiento</Label>
            <Input id="movimiento" name="movimiento" />
          </div>
        </div>
        <div>
          <Label htmlFor="descripcion">Descripción *</Label>
          <Input id="descripcion" name="descripcion" required />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label htmlFor="concepto">Concepto Alegra</Label>
            <Input id="concepto" name="concepto" />
          </div>
          <div>
            <Label htmlFor="origen">Origen/Destino</Label>
            <Input id="origen" name="origen" />
          </div>
          <div>
            <Label htmlFor="cuenta">Cuenta Contable</Label>
            <Input id="cuenta" name="cuenta" />
          </div>
          <div>
            <Label htmlFor="estado">Estado</Label>
            <NativeSelect id="estado" name="estado" defaultValue="Pendiente">
              {ESTADOS.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </NativeSelect>
          </div>
          <div>
            <Label htmlFor="cuentaRef">Ref. Cuenta</Label>
            <Input id="cuentaRef" name="cuentaRef" />
          </div>
          <div>
            <Label htmlFor="nota">Notas</Label>
            <Input id="nota" name="nota" />
          </div>
        </div>

        {state?.error && <p className="text-sm text-red-600">{state.error}</p>}

        <div className="grid grid-cols-2 gap-3 pt-1">
          <Button type="button" variant="secondary" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button type="submit" variant="primary" disabled={pending}>
            Guardar
          </Button>
        </div>
      </form>
    </Dialog>
  );
}
