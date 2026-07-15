export const COMPANIES = [
  { id: "mercury-ltda", name: "Mercury Methods LTDA" },
  { id: "mercury-llc", name: "Mercury Methods LLC" },
  { id: "david-illidge", name: "David Illidge" },
  { id: "azahar-retail", name: "Azahar Retail" },
  { id: "test", name: "TEST" },
] as const;

export const BANCOS = ["Global66 COP", "Global66 USD", "Davivienda", "Bancolombia", "Nequi"] as const;

export const ESTADOS = ["Pendiente", "Conciliado", "En revisión"] as const;
export type Estado = (typeof ESTADOS)[number];
export type Tipo = "cargo" | "abono";
