"use client";

import { useActionState } from "react";
import Link from "next/link";
import { registerAction } from "@/actions/auth";
import { Input, Label } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export function RegisterForm() {
  const [state, action, pending] = useActionState(registerAction, undefined);

  return (
    <form action={action} className="space-y-3">
      <div>
        <Label htmlFor="name">Nombre completo</Label>
        <Input id="name" name="name" placeholder="Nombre completo" />
      </div>
      <div>
        <Label htmlFor="email">Correo</Label>
        <Input id="email" name="email" type="email" placeholder="correo@empresa.com" required />
      </div>
      <div>
        <Label htmlFor="password">Contraseña (mín. 6 caracteres)</Label>
        <Input id="password" name="password" type="password" required minLength={6} />
      </div>
      <div>
        <Label htmlFor="password2">Confirmar contraseña</Label>
        <Input id="password2" name="password2" type="password" required minLength={6} />
      </div>

      {state?.error && <p className="text-sm text-red-600">{state.error}</p>}

      <Button type="submit" variant="primary" className="w-full" disabled={pending}>
        {pending ? "Registrando…" : "Registrarse"}
      </Button>

      <p className="text-center text-xs text-gray-500">
        ¿Ya tienes cuenta?{" "}
        <Link href="/login" className="font-semibold text-[#2c3e50] underline">
          Inicia sesión
        </Link>
      </p>
    </form>
  );
}
