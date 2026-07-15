"use server";

import { and, eq } from "drizzle-orm";
import { refresh } from "next/cache";
import { db } from "@/lib/db";
import { transactions } from "@/lib/db/schema";
import { verifySession } from "@/lib/auth/dal";
import { listTransactions } from "@/lib/queries/transactions";
import { getPeriod } from "@/lib/queries/periods";
import { puedeConciliar } from "@/lib/totals";
import { ESTADOS, type Estado, type Tipo } from "@/lib/companies";
import type { ParsedTx } from "@/lib/import/shared";

export type TxFormState = { error?: string } | undefined;

const EDITABLE_INLINE_FIELDS = ["concepto", "cuenta", "cuentaRef", "origen", "nota", "estado"] as const;
export type EditableInlineField = (typeof EDITABLE_INLINE_FIELDS)[number];

export async function upsertTransactionAction(
  companyId: string,
  periodId: string,
  txId: number | null,
  _prevState: TxFormState,
  formData: FormData,
): Promise<TxFormState> {
  await verifySession();

  const fecha = String(formData.get("fecha") ?? "");
  const descripcion = String(formData.get("descripcion") ?? "").trim();
  const movimiento = String(formData.get("movimiento") ?? "").trim();
  const tipo = String(formData.get("tipo") ?? "cargo") as Tipo;
  const monto = Number(formData.get("monto") ?? 0);
  const concepto = String(formData.get("concepto") ?? "").trim();
  const cuenta = String(formData.get("cuenta") ?? "").trim();
  const cuentaRef = String(formData.get("cuentaRef") ?? "").trim();
  const origen = String(formData.get("origen") ?? "").trim();
  const nota = String(formData.get("nota") ?? "").trim();
  const estado = String(formData.get("estado") ?? "Pendiente") as Estado;

  if (!descripcion) return { error: "Descripción requerida." };
  if (!fecha) return { error: "Fecha requerida." };
  if (!(monto > 0)) return { error: "El monto debe ser mayor a 0." };
  if (tipo !== "cargo" && tipo !== "abono") return { error: "Tipo inválido." };
  if (!ESTADOS.includes(estado)) return { error: "Estado inválido." };

  const values = {
    fecha,
    descripcion,
    movimiento,
    tipo,
    monto: String(monto),
    concepto,
    cuenta,
    cuentaRef,
    origen,
    nota,
    estado,
  };

  if (txId) {
    await db
      .update(transactions)
      .set(values)
      .where(and(eq(transactions.id, txId), eq(transactions.companyId, companyId), eq(transactions.periodId, periodId)));
  } else {
    await db.insert(transactions).values({ companyId, periodId, ...values });
  }

  refresh();
}

export async function updateTransactionFieldAction(
  txId: number,
  field: EditableInlineField,
  value: string,
) {
  await verifySession();
  if (!EDITABLE_INLINE_FIELDS.includes(field)) return;
  if (field === "estado" && !ESTADOS.includes(value as Estado)) return;

  await db
    .update(transactions)
    .set({ [field]: value, updatedAt: new Date() })
    .where(eq(transactions.id, txId));

  refresh();
}

export async function deleteTransactionAction(txId: number) {
  await verifySession();
  await db.delete(transactions).where(eq(transactions.id, txId));
  refresh();
}

export async function conciliarPeriodoAction(companyId: string, periodId: string) {
  await verifySession();

  const period = await getPeriod(companyId, periodId);
  if (!period) return { error: "Período no encontrado." };

  const txs = await listTransactions(companyId, periodId);
  if (!puedeConciliar(period.saldoInicial, txs)) {
    return { error: "Solo se puede conciliar cuando la diferencia es 0." };
  }

  await db
    .update(transactions)
    .set({ estado: "Conciliado", updatedAt: new Date() })
    .where(and(eq(transactions.companyId, companyId), eq(transactions.periodId, periodId), eq(transactions.estado, "Pendiente")));

  refresh();
  return { error: undefined };
}

export async function validarAction(companyId: string, periodId: string) {
  await verifySession();
  const txs = await listTransactions(companyId, periodId);
  refresh();
  return {
    conciliados: txs.filter((t) => t.estado === "Conciliado").length,
    pendientes: txs.filter((t) => t.estado === "Pendiente").length,
  };
}

export async function importTransactionsAction(companyId: string, periodId: string, txs: ParsedTx[]) {
  await verifySession();
  if (txs.length === 0) return;
  await db.insert(transactions).values(
    txs.map((t) => ({
      companyId,
      periodId,
      ...t,
      monto: String(t.monto),
    })),
  );
  refresh();
}
