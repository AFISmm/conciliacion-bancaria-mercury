import "dotenv/config";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { db } from "../lib/db";
import { users, periods, transactions, userSettings } from "../lib/db/schema";
import { eq } from "drizzle-orm";

type OldTx = {
  id: number;
  fecha: string;
  descripcion: string;
  movimiento: string;
  tipo: "cargo" | "abono";
  monto: number;
  concepto?: string;
  cuenta?: string;
  cuentaRef?: string;
  origen?: string;
  contacto?: string; // legacy fallback field, consolidated into origen
  nota?: string;
  estado: "Pendiente" | "Conciliado" | "En revisión";
};

type OldPeriod = {
  id: string;
  nombre: string;
  banco: string;
  cuenta: string;
  saldoInicial: number;
  transactions: OldTx[];
};

type OldCompany = {
  id: string;
  name: string;
  currentPeriodId: string | null;
  periods: Record<string, OldPeriod>;
};

type OldData = {
  currentCompanyId?: string;
  users: Record<string, { name: string; password_hash: string; verified: boolean }>;
  companies: Record<string, OldCompany>;
};

async function main() {
  const jsonPath = process.argv[2] ?? resolve(__dirname, "../../conciliacion_data.json");
  console.log(`Reading ${jsonPath}`);
  const data: OldData = JSON.parse(readFileSync(jsonPath, "utf-8"));

  const emailToUserId = new Map<string, string>();
  for (const [email, u] of Object.entries(data.users ?? {})) {
    const [existing] = await db.select({ id: users.id }).from(users).where(eq(users.email, email)).limit(1);
    if (existing) {
      emailToUserId.set(email, existing.id);
      continue;
    }
    const [row] = await db
      .insert(users)
      .values({ email, name: u.name ?? "", passwordHash: u.password_hash, verified: u.verified ?? false })
      .returning({ id: users.id });
    emailToUserId.set(email, row.id);
    console.log(`  user: ${email}`);
  }

  let periodCount = 0;
  let txCount = 0;

  for (const company of Object.values(data.companies ?? {})) {
    for (const period of Object.values(company.periods ?? {})) {
      const [existing] = await db
        .select({ id: periods.id })
        .from(periods)
        .where(eq(periods.id, period.id))
        .limit(1);
      if (!existing) {
        await db.insert(periods).values({
          id: period.id,
          companyId: company.id,
          nombre: period.nombre,
          banco: period.banco,
          cuenta: period.cuenta ?? "",
          saldoInicial: String(period.saldoInicial ?? 0),
        });
        periodCount++;
      }

      if (period.transactions.length > 0) {
        await db.insert(transactions).values(
          period.transactions.map((t) => ({
            companyId: company.id,
            periodId: period.id,
            fecha: t.fecha,
            descripcion: t.descripcion ?? "",
            movimiento: t.movimiento ?? "",
            tipo: t.tipo,
            monto: String(t.monto),
            concepto: t.concepto ?? "",
            cuenta: t.cuenta ?? "",
            cuentaRef: t.cuentaRef ?? "",
            origen: t.origen ?? t.contacto ?? "",
            nota: t.nota ?? "",
            estado: t.estado,
          })),
        );
        txCount += period.transactions.length;
      }
    }
  }

  for (const [email, userId] of emailToUserId) {
    const company = data.currentCompanyId ? data.companies[data.currentCompanyId] : undefined;
    await db
      .insert(userSettings)
      .values({
        userId,
        currentCompanyId: company?.id ?? null,
        currentPeriodId: company?.currentPeriodId ?? null,
      })
      .onConflictDoNothing();
    console.log(`  settings for ${email}`);
  }

  console.log(`Done — ${periodCount} periods, ${txCount} transactions migrated.`);
  process.exit(0);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
