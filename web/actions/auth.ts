"use server";

import { eq } from "drizzle-orm";
import { redirect } from "next/navigation";
import { db } from "@/lib/db";
import { users } from "@/lib/db/schema";
import { hashPassword, verifyPassword, generateVerificationCode } from "@/lib/auth/password";
import { createSession, destroySession } from "@/lib/auth/session";
import { sendVerificationCode } from "@/lib/email/sendVerificationCode";

const CODE_TTL_MS = 10 * 60 * 1000;

export type AuthState =
  | {
      error?: string;
      info?: string;
      // Shown when Resend isn't configured, mirroring the Streamlit app's
      // fallback of displaying the code directly in the UI.
      devCode?: string;
      needsVerification?: boolean;
      email?: string;
    }
  | undefined;

async function issueVerificationCode(email: string) {
  const code = generateVerificationCode();
  const verificationExpiresAt = new Date(Date.now() + CODE_TTL_MS);
  await db.update(users).set({ verificationCode: code, verificationExpiresAt }).where(eq(users.email, email));
  const { sent } = await sendVerificationCode(email, code);
  return { sent, code };
}

export async function registerAction(_prevState: AuthState, formData: FormData): Promise<AuthState> {
  const name = String(formData.get("name") ?? "").trim();
  const email = String(formData.get("email") ?? "").trim().toLowerCase();
  const password = String(formData.get("password") ?? "");
  const password2 = String(formData.get("password2") ?? "");

  if (!email || !email.includes("@")) return { error: "Correo electrónico inválido." };
  if (password.length < 6) return { error: "La contraseña debe tener al menos 6 caracteres." };
  if (password !== password2) return { error: "Las contraseñas no coinciden." };

  const existing = await db.select({ id: users.id }).from(users).where(eq(users.email, email)).limit(1);
  if (existing.length > 0) return { error: "Este correo ya está registrado." };

  const passwordHash = await hashPassword(password);
  await db.insert(users).values({ email, name, passwordHash, verified: false });

  const { sent, code } = await issueVerificationCode(email);
  redirect(`/verify?email=${encodeURIComponent(email)}${sent ? "" : `&devCode=${code}`}`);
}

export async function loginAction(_prevState: AuthState, formData: FormData): Promise<AuthState> {
  const email = String(formData.get("email") ?? "").trim().toLowerCase();
  const password = String(formData.get("password") ?? "");

  const [user] = await db.select().from(users).where(eq(users.email, email)).limit(1);
  if (!user) return { error: "Correo no registrado." };

  const ok = await verifyPassword(password, user.passwordHash);
  if (!ok) return { error: "Contraseña incorrecta." };

  if (!user.verified) {
    return { error: "Cuenta pendiente de verificación.", needsVerification: true, email };
  }

  await createSession(user.id);
  redirect("/");
}

export async function verifyAction(_prevState: AuthState, formData: FormData): Promise<AuthState> {
  const email = String(formData.get("email") ?? "").trim().toLowerCase();
  const code = String(formData.get("code") ?? "").trim();

  const [user] = await db.select().from(users).where(eq(users.email, email)).limit(1);
  if (!user) return { error: "Usuario no encontrado.", email };
  if (!user.verificationExpiresAt || user.verificationExpiresAt < new Date()) {
    return { error: "Código expirado. Solicite uno nuevo.", email };
  }
  if (user.verificationCode !== code) return { error: "Código incorrecto.", email };

  await db
    .update(users)
    .set({ verified: true, verificationCode: null, verificationExpiresAt: null })
    .where(eq(users.id, user.id));
  await createSession(user.id);
  redirect("/");
}

export async function resendCodeAction(_prevState: AuthState, formData: FormData): Promise<AuthState> {
  const email = String(formData.get("email") ?? "").trim().toLowerCase();
  const [user] = await db.select({ id: users.id }).from(users).where(eq(users.email, email)).limit(1);
  if (!user) return { error: "Usuario no encontrado.", email };

  const { sent, code } = await issueVerificationCode(email);
  return {
    info: sent ? "Código reenviado." : "Resend no configurado — use el código de abajo.",
    devCode: sent ? undefined : code,
    email,
  };
}

export async function logoutAction() {
  await destroySession();
  redirect("/login");
}
