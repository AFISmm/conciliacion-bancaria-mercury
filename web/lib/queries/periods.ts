import "server-only";
import { and, desc, eq } from "drizzle-orm";
import { db } from "@/lib/db";
import { periods } from "@/lib/db/schema";
import type { Period } from "@/lib/types";

function toPeriod(row: typeof periods.$inferSelect): Period {
  return {
    id: row.id,
    companyId: row.companyId,
    nombre: row.nombre,
    banco: row.banco,
    cuenta: row.cuenta,
    saldoInicial: Number(row.saldoInicial),
  };
}

export async function listPeriods(companyId: string): Promise<Period[]> {
  const rows = await db
    .select()
    .from(periods)
    .where(eq(periods.companyId, companyId))
    .orderBy(desc(periods.id));
  return rows.map(toPeriod);
}

export async function getPeriod(companyId: string, periodId: string): Promise<Period | null> {
  const [row] = await db
    .select()
    .from(periods)
    .where(and(eq(periods.companyId, companyId), eq(periods.id, periodId)))
    .limit(1);
  return row ? toPeriod(row) : null;
}
