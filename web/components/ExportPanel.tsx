import type { FilterState } from "@/lib/filters";
import { Button } from "@/components/ui/button";

export function ExportPanel({
  companyId,
  periodId,
  filter,
}: {
  companyId: string;
  periodId: string;
  filter: FilterState;
}) {
  const params = new URLSearchParams({ companyId, periodId, mode: filter.mode });
  if (filter.date) params.set("date", filter.date);
  if (filter.bwMonth) params.set("bwMonth", filter.bwMonth);
  if (filter.bwHalf) params.set("bwHalf", String(filter.bwHalf));

  const hrefFor = (format: string) => `/api/export?${params.toString()}&format=${format}`;

  return (
    <div>
      <p className="mb-2 text-sm font-semibold text-[#2c3e50]">⬇️ Exportar</p>
      <div className="grid grid-cols-3 gap-2">
        <a href={hrefFor("csv")}>
          <Button variant="secondary" className="w-full">
            ⬇️ CSV
          </Button>
        </a>
        <a href={hrefFor("xlsx")}>
          <Button variant="secondary" className="w-full">
            ⬇️ Excel
          </Button>
        </a>
        <a href={hrefFor("pdf")}>
          <Button variant="secondary" className="w-full">
            ⬇️ PDF
          </Button>
        </a>
      </div>
    </div>
  );
}
