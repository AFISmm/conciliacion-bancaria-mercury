"""Cliente para la API REST de Alegra (https://app.alegra.com/api/v1/)."""

import requests
from typing import Optional

BASE_URL = "https://app.alegra.com/api/v1"


class AlegraClient:
    def __init__(self, email: str, token: str):
        self.auth = (email, token)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({"Accept": "application/json"})

    def _get(self, endpoint: str, params: dict = None):
        url = f"{BASE_URL}/{endpoint}"
        resp = self.session.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()

    # ── CUENTAS BANCARIAS ────────────────────────────────────────────
    def get_bank_accounts(self) -> list:
        data = self._get("bank-accounts")
        return data if isinstance(data, list) else data.get("data", [])

    # ── CONTACTOS ────────────────────────────────────────────────────
    def get_contacts(self, query: str = None, limit: int = 200) -> list:
        params = {"limit": limit}
        if query:
            params["name"] = query
        data = self._get("contacts", params=params)
        return data if isinstance(data, list) else data.get("data", [])

    # ── PLAN DE CUENTAS ──────────────────────────────────────────────
    def get_accounts(self, limit: int = 500) -> list:
        data = self._get("accounts", params={"limit": limit})
        return data if isinstance(data, list) else data.get("data", [])

    # ── PAGOS RECIBIDOS (abonos) ─────────────────────────────────────
    def get_payments(
        self,
        date_start: str,
        date_end: str,
        bank_account_id: Optional[int] = None,
        limit: int = 200,
    ) -> list:
        params = {
            "date-start": date_start,
            "date-end": date_end,
            "limit": limit,
        }
        if bank_account_id:
            params["bank-account"] = bank_account_id
        data = self._get("payments", params=params)
        return data if isinstance(data, list) else data.get("data", [])

    # ── COMPRAS / GASTOS (cargos) ────────────────────────────────────
    def get_bills(
        self,
        date_start: str,
        date_end: str,
        limit: int = 200,
    ) -> list:
        params = {
            "date-start": date_start,
            "date-end": date_end,
            "limit": limit,
        }
        data = self._get("bills", params=params)
        return data if isinstance(data, list) else data.get("data", [])

    # ── TEST DE CONEXIÓN ─────────────────────────────────────────────
    def test_connection(self) -> dict:
        """Devuelve info básica de la empresa si las credenciales son válidas."""
        return self._get("company")
