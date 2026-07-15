import ExcelJS from "exceljs";
import type { Transaction } from "@/lib/types";

export async function exportExcel(txs: Transaction[]): Promise<Buffer> {
  const workbook = new ExcelJS.Workbook();
  const sheet = workbook.addWorksheet("Conciliacion");
  sheet.columns = [
    { header: "Fecha", key: "fecha", width: 12 },
    { header: "Descripcion", key: "descripcion", width: 32 },
    { header: "N Movimiento", key: "movimiento", width: 16 },
    { header: "Débito", key: "debito", width: 14 },
    { header: "Crédito", key: "credito", width: 14 },
    { header: "Concepto Alegra", key: "concepto", width: 20 },
    { header: "Cuenta Contable", key: "cuenta", width: 16 },
    { header: "Ref Cuenta", key: "cuentaRef", width: 18 },
    { header: "Origen/Destino", key: "origen", width: 20 },
    { header: "Notas", key: "nota", width: 20 },
    { header: "Estado", key: "estado", width: 14 },
  ];

  for (const t of txs) {
    sheet.addRow({
      fecha: t.fecha,
      descripcion: t.descripcion,
      movimiento: t.movimiento,
      debito: t.tipo === "cargo" ? t.monto : 0,
      credito: t.tipo === "abono" ? t.monto : 0,
      concepto: t.concepto,
      cuenta: t.cuenta,
      cuentaRef: t.cuentaRef,
      origen: t.origen,
      nota: t.nota,
      estado: t.estado,
    });
  }

  sheet.getRow(1).font = { bold: true };
  const buf = await workbook.xlsx.writeBuffer();
  return Buffer.from(buf);
}
