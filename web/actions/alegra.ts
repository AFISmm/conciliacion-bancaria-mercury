"use server";

import { verifySession } from "@/lib/auth/dal";
import { AlegraClient } from "@/lib/alegra/client";

export async function testAlegraConnectionAction(email: string, token: string) {
  await verifySession();
  if (!email || !token) return { ok: false, message: "Credenciales incompletas." };
  try {
    const client = new AlegraClient(email, token);
    const company = await client.testConnection();
    return { ok: true, message: company.name ? `Conectado — ${company.name}` : "Conectado." };
  } catch (err) {
    return { ok: false, message: err instanceof Error ? err.message : "Error de conexión." };
  }
}
