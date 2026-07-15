import type { Transaction } from "./types";

export type FilterMode = "month" | "day" | "week" | "biweek";
export type FilterState = {
  mode: FilterMode;
  date?: string;
  bwMonth?: string;
  bwHalf?: 1 | 2;
};

// Mirrors app.py's filtered_txs(): "month" (default) returns everything,
// "day"/"week"/"biweek" narrow by the fecha string.
export function filterTransactions(txs: Transaction[], filter: FilterState): Transaction[] {
  if (filter.mode === "day" && filter.date) {
    return txs.filter((t) => t.fecha === filter.date);
  }
  if (filter.mode === "week" && filter.date) {
    const d = new Date(`${filter.date}T00:00:00`);
    const dayIdx = (d.getDay() + 6) % 7; // Monday = 0
    const mon = new Date(d);
    mon.setDate(d.getDate() - dayIdx);
    const sun = new Date(mon);
    sun.setDate(mon.getDate() + 6);
    return txs.filter((t) => {
      const td = new Date(`${t.fecha}T00:00:00`);
      return td >= mon && td <= sun;
    });
  }
  if (filter.mode === "biweek" && filter.bwMonth) {
    const half = filter.bwHalf ?? 1;
    return txs.filter((t) => {
      if (!t.fecha.startsWith(filter.bwMonth!)) return false;
      const day = Number(t.fecha.slice(8, 10));
      return half === 1 ? day <= 15 : day > 15;
    });
  }
  return txs;
}
