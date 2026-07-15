"use client";

import { useActionState } from "react";
import { verifyAction, resendCodeAction } from "@/actions/auth";
import { Input, Label } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export function VerifyForm({ email, initialDevCode }: { email: string; initialDevCode?: string }) {
  const [verifyState, verifyDispatch, verifyPending] = useActionState(verifyAction, undefined);
  const [resendState, resendDispatch, resendPending] = useActionState(resendCodeAction, undefined);

  // Once a resend has been attempted, trust its result exclusively — an
  // undefined devCode there means the email actually sent.
  const devCode = resendState ? resendState.devCode : initialDevCode;

  return (
    <div className="space-y-4">
      {devCode ? (
        <div className="rounded-lg bg-gray-100 p-4 text-center">
          <p className="text-xs text-gray-500">Resend no configurado — use el código de abajo:</p>
          <p className="mt-1 text-3xl font-bold tracking-[0.3em] text-[#2c3e50]">{devCode}</p>
          <p className="mt-1 text-xs text-gray-500">Válido 10 min</p>
        </div>
      ) : (
        <p className="text-center text-sm text-gray-600">
          📧 Código enviado a <strong>{email}</strong>
        </p>
      )}

      <form action={verifyDispatch} className="space-y-3">
        <input type="hidden" name="email" value={email} />
        <div>
          <Label htmlFor="code">Código de 6 dígitos</Label>
          <Input id="code" name="code" maxLength={6} placeholder="123456" required />
        </div>
        {verifyState?.error && <p className="text-sm text-red-600">{verifyState.error}</p>}
        <Button type="submit" variant="primary" className="w-full" disabled={verifyPending}>
          {verifyPending ? "Verificando…" : "Verificar cuenta"}
        </Button>
      </form>

      <form action={resendDispatch}>
        <input type="hidden" name="email" value={email} />
        <Button type="submit" variant="secondary" className="w-full" disabled={resendPending}>
          {resendPending ? "Enviando…" : "🔄 Reenviar código"}
        </Button>
      </form>
      {resendState?.info && !devCode && <p className="text-center text-xs text-green-700">{resendState.info}</p>}
    </div>
  );
}
