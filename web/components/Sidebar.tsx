"use client";

import { useTransition } from "react";
import { setCurrentCompanyAction, setCurrentPeriodAction, saveAlegraCredentialsAction } from "@/actions/settings";
import { setPeriodBancoAction } from "@/actions/periods";
import { logoutAction } from "@/actions/auth";
import { BANCOS } from "@/lib/companies";
import type { Company, Period } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input, Label, NativeSelect } from "@/components/ui/input";

export function Sidebar({
  userName,
  companies,
  currentCompanyId,
  periods,
  currentPeriod,
  alegraEmail,
  alegraToken,
  onNewPeriod,
  onEditPeriod,
}: {
  userName: string;
  companies: Company[];
  currentCompanyId: string | null;
  periods: Period[];
  currentPeriod: Period | null;
  alegraEmail: string;
  alegraToken: string;
  onNewPeriod: () => void;
  onEditPeriod: () => void;
}) {
  const [, startTransition] = useTransition();
  const currentCompanyName = companies.find((c) => c.id === currentCompanyId)?.name ?? "";

  return (
    <aside className="flex w-64 shrink-0 flex-col gap-4 border-r border-gray-200 bg-white p-4">
      <div>
        <p className="text-sm font-bold text-[#2c3e50]">{currentCompanyName || "Portal de Conciliaciones"}</p>
        <p className="mt-1 text-xs text-gray-500">👤 {userName}</p>
        <form action={logoutAction}>
          <Button type="submit" variant="secondary" className="mt-2 w-full">
            Cerrar sesión
          </Button>
        </form>
      </div>

      <hr className="border-gray-200" />

      <div>
        <h3 className="mb-2 text-xs font-bold uppercase tracking-wide text-gray-500">🏢 Empresas</h3>
        <div className="flex flex-col gap-1">
          {companies.map((c) => {
            const active = c.id === currentCompanyId;
            return (
              <Button
                key={c.id}
                variant={active ? "primary" : "secondary"}
                className="w-full justify-start"
                onClick={() => startTransition(() => setCurrentCompanyAction(c.id))}
              >
                {active ? "▶  " : ""}
                {c.name}
              </Button>
            );
          })}
        </div>
      </div>

      {currentCompanyId && (
        <>
          <hr className="border-gray-200" />

          <div>
            <h3 className="mb-2 text-xs font-bold uppercase tracking-wide text-gray-500">📅 Período</h3>
            {periods.length > 0 ? (
              <NativeSelect
                value={currentPeriod?.id ?? ""}
                onChange={(e) => startTransition(() => setCurrentPeriodAction(e.target.value))}
              >
                {periods.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.nombre}
                  </option>
                ))}
              </NativeSelect>
            ) : (
              <p className="text-xs text-gray-500">Sin períodos. Use ➕ Nuevo.</p>
            )}
            <div className="mt-2 grid grid-cols-2 gap-2">
              <Button variant="secondary" className="w-full" onClick={onNewPeriod}>
                ➕ Nuevo
              </Button>
              <Button variant="secondary" className="w-full" onClick={onEditPeriod} disabled={!currentPeriod}>
                ✏️ Editar
              </Button>
            </div>
          </div>

          {currentPeriod && (
            <>
              <hr className="border-gray-200" />
              <div>
                <h3 className="mb-2 text-xs font-bold uppercase tracking-wide text-gray-500">🏦 Banco</h3>
                <NativeSelect
                  value={currentPeriod.banco}
                  onChange={(e) =>
                    startTransition(() => setPeriodBancoAction(currentCompanyId, currentPeriod.id, e.target.value))
                  }
                >
                  {BANCOS.map((b) => (
                    <option key={b} value={b}>
                      {b}
                    </option>
                  ))}
                </NativeSelect>
              </div>
            </>
          )}

          <hr className="border-gray-200" />

          <details className="text-sm">
            <summary className="cursor-pointer text-xs font-bold uppercase tracking-wide text-gray-500">
              🔗 Alegra
            </summary>
            <p className="mt-1 text-xs text-gray-500">
              {alegraEmail && alegraToken ? "✅ Credenciales OK" : "⚙️ Sin configurar"}
            </p>
            <form action={saveAlegraCredentialsAction} className="mt-2 space-y-2">
              <div>
                <Label htmlFor="alegraEmail">Email Alegra</Label>
                <Input id="alegraEmail" name="alegraEmail" defaultValue={alegraEmail} />
              </div>
              <div>
                <Label htmlFor="alegraToken">Token API</Label>
                <Input id="alegraToken" name="alegraToken" type="password" defaultValue={alegraToken} />
              </div>
              <Button type="submit" variant="primary" className="w-full">
                💾 Guardar
              </Button>
            </form>
          </details>
        </>
      )}
    </aside>
  );
}
