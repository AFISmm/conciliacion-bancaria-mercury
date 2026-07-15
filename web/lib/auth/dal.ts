import "server-only";
import { cache } from "react";
import { redirect } from "next/navigation";
import { eq } from "drizzle-orm";
import { db } from "@/lib/db";
import { users, sessions } from "@/lib/db/schema";
import { getSessionPayload } from "./session";

// Secure check: cross-references the DB session row (not just the signed
// cookie) so logout / expiry are enforced server-side, per Next.js's DAL
// pattern. cache() dedupes this across a single render pass.
export const verifySession = cache(async () => {
  const payload = await getSessionPayload();
  if (!payload) redirect("/login");

  const [row] = await db
    .select({ userId: sessions.userId, expiresAt: sessions.expiresAt })
    .from(sessions)
    .where(eq(sessions.id, payload.sessionId))
    .limit(1);

  if (!row || row.expiresAt < new Date()) redirect("/login");

  return { userId: row.userId };
});

export const getCurrentUser = cache(async () => {
  const { userId } = await verifySession();
  const [user] = await db
    .select({ id: users.id, email: users.email, name: users.name })
    .from(users)
    .where(eq(users.id, userId))
    .limit(1);
  return user ?? null;
});
