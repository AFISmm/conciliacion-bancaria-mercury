"use client";

import { useActionState, useEffect, useRef, useTransition } from "react";
import { Dialog } from "@/components/ui/dialog";
import { createPeriodAction, updatePeriodAction, deletePeriodAction } from "@/actions/periods";
import { BANCOS } from "@/lib/companies";
import type { Period } from "@/lib/types";
import { Input, Label, NativeSelect } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export function PeriodDialog({
  open,
  onOpenChange,
  companyId,
  period,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  companyId: string;
  period: Period | null;
}) {
  const action = period
    ? updatePeriodAction.bind(null, companyId, period.id)
    : createPeriodAction.bind(null, companyId);
  const [state, dispatch, pending] = useActionState(action, undefined);
  const [isDeletePending, startDeleteTransition] = useTransition();
  const prevPending = useRef(pending);

  useEffect(() => {
    if (prevPending.current && !pending && !state?.error) onOpenChange(false);
    prevPending.current = pending;
  }, [pending, state, onOpenChange]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange} title={period ? "Editar período" : "Nuevo período"}>
      <form action={dispatch} className="space-y-3">
        <div>
          <Label htmlFor="nombre">Nombre *</Label>
          <Input id="nombre" name="nombre" defaultValue={period?.nombre ?? ""} required />
        </div>
        <div>
          <Label htmlFor="id">ID período (YYYY-MM)</Label>
          <Input
            id="id"
            name="id"
            defaultValue={period?.id ?? ""}
            placeholder="2026-07"
            maxLength={7}
            disabled={!!period}
            required={!period}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label htmlFor="saldoInicial">Saldo inicial ($)</Label>
            <Input id="saldoInicial" name="saldoInicial" type="number" step="0.01" defaultValue={period?.saldoInicial ?? 0} />
          </div>
          <div>
            <Label htmlFor="banco">Banco</Label>
            <NativeSelect id="banco" name="banco" defaultValue={period?.banco ?? BANCOS[0]}>
              {BANCOS.map((b) => (
                <option key={b} value={b}>
                  {b}
                </option>
              ))}
            </NativeSelect>
          </div>
        </div>
        <div>
          <Label htmlFor="cuenta">N° Cuenta</Label>
          <Input id="cuenta" name="cuenta" defaultValue={period?.cuenta ?? ""} />
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

        {period && (
          <Button
            type="button"
            variant="danger"
            className="w-full"
            disabled={isDeletePending}
            onClick={() =>
              startDeleteTransition(async () => {
                await deletePeriodAction(companyId, period.id);
                onOpenChange(false);
              })
            }
          >
            🗑 Eliminar período
          </Button>
        )}
      </form>
    </Dialog>
  );
}
