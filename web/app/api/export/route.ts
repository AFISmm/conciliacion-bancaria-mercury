import type { NextRequest } from "next/server";
import { verifySession } from "@/lib/auth/dal";
import { listTransactions } from "@/lib/queries/transactions";
import { getPeriod } from "@/lib/queries/periods";
import { filterTransactions, type FilterMode } from "@/lib/filters";
import { exportCsv } from "@/lib/export/csv";
import { exportExcel } from "@/lib/export/excel";
import { exportPdf } from "@/lib/export/pdf";

export async function GET(req: NextRequest) {
  await verifySession();

  const { searchParams } = req.nextUrl;
  const format = searchParams.get("format");
  const companyId = searchParams.get("companyId");
  const periodId = searchParams.get("periodId");
  if (!companyId || !periodId) {
    return new Response("Missing companyId/periodId", { status: 400 });
  }

  const period = await getPeriod(companyId, periodId);
  if (!period) return new Response("Period not found", { status: 404 });

  const all = await listTransactions(companyId, periodId);
  const bwHalf = searchParams.get("bwHalf");
  const txs = filterTransactions(all, {
    mode: (searchParams.get("mode") as FilterMode) ?? "month",
    date: searchParams.get("date") ?? undefined,
    bwMonth: searchParams.get("bwMonth") ?? undefined,
    bwHalf: bwHalf === "1" || bwHalf === "2" ? (Number(bwHalf) as 1 | 2) : undefined,
  });

  const today = new Date().toISOString().slice(0, 10);

  if (format === "csv") {
    return new Response(exportCsv(txs), {
      headers: {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": `attachment; filename="conciliacion_${today}.csv"`,
      },
    });
  }
  if (format === "xlsx") {
    const buf = await exportExcel(txs);
    return new Response(new Uint8Array(buf), {
      headers: {
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "Content-Disposition": `attachment; filename="conciliacion_${today}.xlsx"`,
      },
    });
  }
  if (format === "pdf") {
    const bytes = await exportPdf(txs, period);
    return new Response(new Uint8Array(bytes), {
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": `attachment; filename="conciliacion_${today}.pdf"`,
      },
    });
  }

  return new Response("Invalid format", { status: 400 });
}
