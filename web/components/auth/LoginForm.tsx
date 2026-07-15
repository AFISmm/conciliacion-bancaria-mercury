"use client";

import { useActionState } from "react";
import Link from "next/link";
import { loginAction } from "@/actions/auth";
import { Input, Label } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export function LoginForm() {
  const [state, action, pending] = useActionState(loginAction, undefined);

  return (
    <form action={action} className="space-y-3">
      <div>
        <Label htmlFor="email">Correo</Label>
        <Input id="email" name="email" type="email" placeholder="correo@empresa.com" required />
      </div>
      <div>
        <Label htmlFor="password">Contraseña</Label>
        <Input id="password" name="password" type="password" required />
      </div>

      {state?.error && (
        <p className="text-sm text-red-600">
          {state.error}
          {state.needsVerification && (
            <>
              {" "}
              <Link href={`/verify?email=${encodeURIComponent(state.email ?? "")}`} className="font-semibold underline">
                Verificar cuenta
              </Link>
            </>
          )}
        </p>
      )}

      <Button type="submit" variant="primary" className="w-full" disabled={pending}>
        {pending ? "Ingresando…" : "Ingresar"}
      </Button>

      <p className="text-center text-xs text-gray-500">
        ¿No tienes cuenta?{" "}
        <Link href="/register" className="font-semibold text-[#2c3e50] underline">
          Regístrate
        </Link>
      </p>
    </form>
  );
}
