import type { NextRequest } from "next/server";
import { verifySession } from "@/lib/auth/dal";
import { parseCsv } from "@/lib/import/csv";
import { parseExcel } from "@/lib/import/excel";
import { parsePdf } from "@/lib/import/pdf";

export async function POST(req: NextRequest) {
  await verifySession();

  const formData = await req.formData();
  const file = formData.get("file");
  const kind = formData.get("kind");

  if (!(file instanceof File)) {
    return Response.json({ error: "No se recibió ningún archivo." }, { status: 400 });
  }

  try {
    if (kind === "csv") {
      return Response.json(parseCsv(await file.text()));
    }
    if (kind === "excel") {
      return Response.json(await parseExcel(await file.arrayBuffer()));
    }
    if (kind === "pdf") {
      return Response.json(await parsePdf(await file.arrayBuffer()));
    }
    return Response.json({ error: "Tipo de archivo inválido." }, { status: 400 });
  } catch (err) {
    return Response.json({ error: err instanceof Error ? err.message : "Error al procesar el archivo." }, { status: 500 });
  }
}
