import type { Estado, Tipo } from "./companies";

export type Transaction = {
  id: number;
  companyId: string;
  periodId: string;
  fecha: string;
  descripcion: string;
  movimiento: string;
  tipo: Tipo;
  monto: number;
  concepto: string;
  cuenta: string;
  cuentaRef: string;
  origen: string;
  nota: string;
  estado: Estado;
};

export type Period = {
  id: string;
  companyId: string;
  nombre: string;
  banco: string;
  cuenta: string;
  saldoInicial: number;
};

export type Company = {
  id: string;
  name: string;
};
