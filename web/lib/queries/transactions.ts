import "server-only";
import { and, asc, eq } from "drizzle-orm";
import { db } from "@/lib/db";
import { transactions } from "@/lib/db/schema";
import type { Transaction } from "@/lib/types";

function toTx(row: typeof transactions.$inferSelect): Transaction {
  return {
    id: row.id,
    companyId: row.companyId,
    periodId: row.periodId,
    fecha: row.fecha,
    descripcion: row.descripcion,
    movimiento: row.movimiento,
    tipo: row.tipo as Transaction["tipo"],
    monto: Number(row.monto),
    concepto: row.concepto,
    cuenta: row.cuenta,
    cuentaRef: row.cuentaRef,
    origen: row.origen,
    nota: row.nota,
    estado: row.estado as Transaction["estado"],
  };
}

export async function listTransactions(companyId: string, periodId: string): Promise<Transaction[]> {
  const rows = await db
    .select()
    .from(transactions)
    .where(and(eq(transactions.companyId, companyId), eq(transactions.periodId, periodId)))
    .orderBy(asc(transactions.fecha), asc(transactions.id));
  return rows.map(toTx);
}
