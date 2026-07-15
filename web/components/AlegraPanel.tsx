"use client";

import { useState, useTransition } from "react";
import { testAlegraConnectionAction } from "@/actions/alegra";
import { Button } from "@/components/ui/button";

export function AlegraPanel({ email, token }: { email: string; token: string }) {
  const [result, setResult] = useState<{ ok: boolean; message: string } | null>(null);
  const [isPending, startTransition] = useTransition();
  const configured = Boolean(email && token);

  return (
    <div className="max-w-xl">
      <h3 className="mb-2 text-sm font-semibold text-[#2c3e50]">🔗 Integración con Alegra</h3>
      {configured ? (
        <p className="rounded-md bg-green-50 px-3 py-2 text-sm text-green-700">
          ✅ Credenciales configuradas — <strong>{email}</strong>
        </p>
      ) : (
        <p className="rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-700">
          ⚙️ Credenciales no configuradas. Configure en el panel lateral.
        </p>
      )}

      <div className="mt-4 text-sm text-gray-700">
        <p className="font-semibold">Para conectar:</p>
        <ol className="ml-4 list-decimal">
          <li>Alegra → Configuración → Mi perfil → Token de API</li>
          <li>Copie el token y péguelo en Panel lateral → Alegra → Configurar</li>
        </ol>
      </div>

      {configured && (
        <div className="mt-4">
          <Button
            variant="secondary"
            disabled={isPending}
            onClick={() =>
              startTransition(async () => {
                setResult(await testAlegraConnectionAction(email, token));
              })
            }
          >
            Probar conexión
          </Button>
          {result && (
            <p className={`mt-2 text-sm ${result.ok ? "text-green-700" : "text-red-600"}`}>{result.message}</p>
          )}
        </div>
      )}
    </div>
  );
}
