"use server";

import { and, eq } from "drizzle-orm";
import { refresh } from "next/cache";
import { db } from "@/lib/db";
import { periods, userSettings } from "@/lib/db/schema";
import { verifySession } from "@/lib/auth/dal";
import { BANCOS } from "@/lib/companies";

export type PeriodFormState = { error?: string } | undefined;

export async function createPeriodAction(
  companyId: string,
  _prevState: PeriodFormState,
  formData: FormData,
): Promise<PeriodFormState> {
  await verifySession();

  const id = String(formData.get("id") ?? "").trim();
  const nombre = String(formData.get("nombre") ?? "").trim();
  const banco = String(formData.get("banco") ?? "");
  const cuenta = String(formData.get("cuenta") ?? "").trim();
  const saldoInicial = Number(formData.get("saldoInicial") ?? 0);

  if (!nombre) return { error: "Nombre requerido." };
  if (!/^\d{4}-\d{2}$/.test(id)) return { error: "ID inválido (formato YYYY-MM)." };
  if (!BANCOS.includes(banco as (typeof BANCOS)[number])) return { error: "Banco inválido." };

  const existing = await db
    .select({ id: periods.id })
    .from(periods)
    .where(and(eq(periods.companyId, companyId), eq(periods.id, id)))
    .limit(1);
  if (existing.length > 0) return { error: "Ya existe un período con ese ID." };

  await db.insert(periods).values({ id, companyId, nombre, banco, cuenta, saldoInicial: String(saldoInicial) });

  const { userId } = await verifySession();
  await db
    .insert(userSettings)
    .values({ userId, currentCompanyId: companyId, currentPeriodId: id })
    .onConflictDoUpdate({ target: userSettings.userId, set: { currentCompanyId: companyId, currentPeriodId: id } });

  refresh();
}

export async function updatePeriodAction(
  companyId: string,
  periodId: string,
  _prevState: PeriodFormState,
  formData: FormData,
): Promise<PeriodFormState> {
  await verifySession();

  const nombre = String(formData.get("nombre") ?? "").trim();
  const banco = String(formData.get("banco") ?? "");
  const cuenta = String(formData.get("cuenta") ?? "").trim();
  const saldoInicial = Number(formData.get("saldoInicial") ?? 0);

  if (!nombre) return { error: "Nombre requerido." };
  if (!BANCOS.includes(banco as (typeof BANCOS)[number])) return { error: "Banco inválido." };

  await db
    .update(periods)
    .set({ nombre, banco, cuenta, saldoInicial: String(saldoInicial) })
    .where(and(eq(periods.companyId, companyId), eq(periods.id, periodId)));

  refresh();
}

export async function setPeriodBancoAction(companyId: string, periodId: string, banco: string) {
  await verifySession();
  if (!BANCOS.includes(banco as (typeof BANCOS)[number])) return;
  await db.update(periods).set({ banco }).where(and(eq(periods.companyId, companyId), eq(periods.id, periodId)));
  refresh();
}

export async function deletePeriodAction(companyId: string, periodId: string) {
  const { userId } = await verifySession();
  await db.delete(periods).where(and(eq(periods.companyId, companyId), eq(periods.id, periodId)));

  const remaining = await db.select({ id: periods.id }).from(periods).where(eq(periods.companyId, companyId)).limit(1);
  await db
    .insert(userSettings)
    .values({ userId, currentCompanyId: companyId, currentPeriodId: remaining[0]?.id ?? null })
    .onConflictDoUpdate({
      target: userSettings.userId,
      set: { currentCompanyId: companyId, currentPeriodId: remaining[0]?.id ?? null },
    });

  refresh();
}
