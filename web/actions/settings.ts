"use server";

import { refresh } from "next/cache";
import { db } from "@/lib/db";
import { userSettings } from "@/lib/db/schema";
import { verifySession } from "@/lib/auth/dal";

async function upsertSettings(userId: string, values: Partial<typeof userSettings.$inferInsert>) {
  await db
    .insert(userSettings)
    .values({ userId, ...values })
    .onConflictDoUpdate({ target: userSettings.userId, set: values });
}

export async function setCurrentCompanyAction(companyId: string) {
  const { userId } = await verifySession();
  await upsertSettings(userId, { currentCompanyId: companyId, currentPeriodId: null });
  refresh();
}

export async function setCurrentPeriodAction(periodId: string) {
  const { userId } = await verifySession();
  await upsertSettings(userId, { currentPeriodId: periodId });
  refresh();
}

export async function saveAlegraCredentialsAction(formData: FormData) {
  const { userId } = await verifySession();
  const alegraEmail = String(formData.get("alegraEmail") ?? "").trim();
  const alegraToken = String(formData.get("alegraToken") ?? "").trim();
  await upsertSettings(userId, { alegraEmail, alegraToken });
  refresh();
}
