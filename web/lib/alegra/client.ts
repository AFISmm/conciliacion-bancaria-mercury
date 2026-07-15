import "server-only";

const BASE_URL = "https://app.alegra.com/api/v1";

export class AlegraClient {
  private authHeader: string;

  constructor(email: string, token: string) {
    this.authHeader = `Basic ${Buffer.from(`${email}:${token}`).toString("base64")}`;
  }

  private async get<T>(endpoint: string, params: Record<string, string | number | undefined> = {}): Promise<T> {
    const url = new URL(`${BASE_URL}/${endpoint}`);
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined) url.searchParams.set(key, String(value));
    }
    const res = await fetch(url, {
      headers: { Accept: "application/json", Authorization: this.authHeader },
      signal: AbortSignal.timeout(15_000),
    });
    if (!res.ok) throw new Error(`Alegra API error ${res.status}: ${res.statusText}`);
    return res.json();
  }

  getBankAccounts() {
    return this.get<unknown[]>("bank-accounts");
  }

  getContacts(query?: string, limit = 200) {
    return this.get<unknown[]>("contacts", { limit, name: query });
  }

  getAccounts(limit = 500) {
    return this.get<unknown[]>("accounts", { limit });
  }

  getPayments(dateStart: string, dateEnd: string, bankAccountId?: number, limit = 200) {
    return this.get<unknown[]>("payments", {
      "date-start": dateStart,
      "date-end": dateEnd,
      "bank-account": bankAccountId,
      limit,
    });
  }

  getBills(dateStart: string, dateEnd: string, limit = 200) {
    return this.get<unknown[]>("bills", { "date-start": dateStart, "date-end": dateEnd, limit });
  }

  testConnection() {
    return this.get<{ name?: string }>("company");
  }
}
