import "server-only";
import { eq } from "drizzle-orm";
import { db } from "@/lib/db";
import { userSettings } from "@/lib/db/schema";

export type UserSettings = {
  alegraEmail: string;
  alegraToken: string;
  currentCompanyId: string | null;
  currentPeriodId: string | null;
};

const DEFAULTS: UserSettings = {
  alegraEmail: "",
  alegraToken: "",
  currentCompanyId: null,
  currentPeriodId: null,
};

export async function getUserSettings(userId: string): Promise<UserSettings> {
  const [row] = await db.select().from(userSettings).where(eq(userSettings.userId, userId)).limit(1);
  if (!row) return DEFAULTS;
  return {
    alegraEmail: row.alegraEmail,
    alegraToken: row.alegraToken,
    currentCompanyId: row.currentCompanyId,
    currentPeriodId: row.currentPeriodId,
  };
}
