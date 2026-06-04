"""Conciliación Bancaria – Mercury Methods · Streamlit + Alegra."""

import json
import calendar
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

# ── CONFIGURACIÓN (debe ser la primera llamada a st) ─────────────────────
st.set_page_config(
    page_title="Conciliación Bancaria – Mercury Methods",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CONSTANTES ───────────────────────────────────────────────────────────
# En local: guarda junto al app.py. En Streamlit Cloud: usa /tmp (sesión).
_local_file = Path(__file__).parent / "conciliacion_data.json"
try:
    _local_file.parent.stat()
    _local_file.touch(exist_ok=True)
    DATA_FILE = _local_file
except (PermissionError, OSError):
    DATA_FILE = Path("/tmp") / "conciliacion_data.json"
BANCOS    = ["Global66 COP", "Global66 USD", "Davivienda"]
ESTADOS   = ["Pendiente", "Conciliado", "En revisión"]

# ── CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
div[data-testid="metric-container"] {
    background:#fff;border:1px solid #e0e0e0;border-radius:8px;
    padding:10px 14px;box-shadow:0 2px 8px rgba(0,0,0,.08);
}
[data-testid="stMetricLabel"]  {font-size:.72rem;color:#757575;}
[data-testid="stMetricValue"]  {font-size:1.05rem;font-weight:700;}
.block-container {padding-top:.8rem !important;}
</style>
""", unsafe_allow_html=True)

# ── MODELO DE DATOS ──────────────────────────────────────────────────────
def _next_id() -> int:
    st.session_state.setdefault("_id_ctr", 1000)
    st.session_state["_id_ctr"] += 1
    return st.session_state["_id_ctr"]


def make_tx(fecha, desc, mov, tipo, monto,
            concepto="", cuenta="", cuenta_ref="", contacto="",
            nota="", estado="Pendiente", tx_id=None) -> dict:
    return {
        "id":          tx_id if tx_id is not None else _next_id(),
        "fecha":       str(fecha),
        "descripcion": str(desc),
        "movimiento":  str(mov),
        "tipo":        tipo,
        "monto":       float(monto),
        "concepto":    concepto,
        "cuenta":      cuenta,
        "cuentaRef":   cuenta_ref,
        "contacto":    contacto,
        "nota":        nota,
        "estado":      estado,
    }


def _marzo_2026_txs() -> list:
    rows = [
        ("2026-03-03","Otro Movimiento de Retiro","28831783","cargo",6405200.00,"","Según destinatario","22xx / 5105xx / 3710xx","","","Pendiente"),
        ("2026-03-03","GMF","11383614","cargo",12003.56,"Impuestos no acreditables","54100501","Gastos por impuestos no acreditables","Global66","GMF 4x1000 retiro 28831783","Conciliado"),
        ("2026-03-03","Otro Movimiento de Depósito","62012","abono",18795319.37,"","","13050501 / 23550001","","","Pendiente"),
        ("2026-03-05","GMF","11454399","cargo",1104.32,"Impuestos no acreditables","54100501","Gastos por impuestos no acreditables","Global66","GMF Comcel 11160098","Conciliado"),
        ("2026-03-05","Compra Comcel Domiciliacion M","11160098 (T:5829)","cargo",276080.00,"Teléfono","51353501","Servicios / Teléfono","Comcel / Claro","","Conciliado"),
        ("2026-03-05","GMF","11454421","cargo",179.46,"Impuestos no acreditables","54100501","Gastos por impuestos no acreditables","Global66","GMF Comcel 11160123","Conciliado"),
        ("2026-03-05","Compra Comcel Domiciliacion M","11160123 (T:5829)","cargo",44864.00,"Teléfono","51353501","Servicios / Teléfono","Comcel / Claro","","Conciliado"),
        ("2026-03-05","Otro Movimiento de Depósito","28992772","abono",42143.91,"","","13050501 / 23550001","","","Pendiente"),
        ("2026-03-06","Otro Movimiento de Depósito","6937581 (T:5829)","abono",56563.15,"","","13050501 / 23550001","","","Pendiente"),
        ("2026-03-06","GMF","11519323","cargo",226.26,"Impuestos no acreditables","54100501","Gastos por impuestos no acreditables","Global66","GMF Microsoft 11192582","Conciliado"),
        ("2026-03-06","Compra Microsoft#g143376191","11192582 (T:5829)","cargo",56563.15,"Software contables","51959501","Servicios online / Software","Microsoft","","Conciliado"),
        ("2026-03-06","Otro Movimiento de Depósito","6937612 (T:5829)","abono",55505.39,"","","","","","Pendiente"),
        ("2026-03-06","GMF","11519380","cargo",222.03,"Impuestos no acreditables","54100501","Gastos por impuestos no acreditables","Global66","GMF Microsoft 11192629","Conciliado"),
        ("2026-03-06","Compra Microsoft#g144371480","11192629 (T:5829)","cargo",55505.39,"Software contables","51959501","Servicios online / Software","Microsoft","","Conciliado"),
        ("2026-03-06","Otro Movimiento de Depósito","6937668 (T:5829)","abono",148467.50,"","","","","","Pendiente"),
        ("2026-03-06","GMF","11519447","cargo",593.87,"Impuestos no acreditables","54100501","Gastos por impuestos no acreditables","Global66","GMF Microsoft 11192676","Conciliado"),
        ("2026-03-06","Compra Microsoft#g144431070","11192676 (T:5829)","cargo",148467.50,"Software contables","51959501","Servicios online / Software","Microsoft","","Conciliado"),
        ("2026-03-07","Otro Movimiento de Depósito","29176285","abono",3316.83,"","","","","","Pendiente"),
        ("2026-03-13","GMF","11721009","cargo",185.89,"Impuestos no acreditables","54100501","","Global66","GMF Comcel 11353946","Conciliado"),
        ("2026-03-13","Compra Comcel Domiciliacion M","11353946 (T:5829)","cargo",46472.00,"Teléfono","51353501","Servicios / Teléfono","Comcel / Claro","","Conciliado"),
        ("2026-03-13","Otro Movimiento de Retiro","7050429","cargo",800000.00,"","","22xx / 5105xx / 3710xx","","","Pendiente"),
        ("2026-03-13","Otro Movimiento de Retiro","7050430","cargo",800000.00,"","","22xx / 5105xx / 3710xx","","","Pendiente"),
        ("2026-03-13","GMF","11728508","cargo",3200.00,"Impuestos no acreditables","54100501","","Global66","GMF retiro 7050429/7050430","Conciliado"),
        ("2026-03-13","Otro Movimiento de Retiro","29472130","cargo",2400000.00,"","","22xx / 5105xx / 3710xx","","","Pendiente"),
        ("2026-03-13","Otro Movimiento de Retiro","29472131","cargo",800000.00,"","","","","","Pendiente"),
        ("2026-03-13","GMF","11728511 / 11728512 / 11728513","cargo",16000.00,"Impuestos no acreditables","54100501","","Global66","GMF retiros grandes 13/03","Conciliado"),
        ("2026-03-13","IMPUESTO IVA","11728514 / 11728515","cargo",845.12,"IVA descontable","51157001","IVA descontable","Global66","IVA cobro por retiro 13/03","Conciliado"),
        ("2026-03-13","COBRO POR RETIRO","11728516 / 11728517","cargo",4448.00,"Comisiones bancarias","53051501","Comisiones bancarias","Global66","Comisión retiro 13/03","Conciliado"),
        ("2026-03-15","GMF","11793429","cargo",763.97,"Impuestos no acreditables","54100501","","Global66","GMF Movistar 11413473","Conciliado"),
        ("2026-03-15","Compra Movistar Pagosepayco","11413473 (T:5829)","cargo",190992.00,"Teléfono","51353501","Servicios / Teléfono","Movistar Colombia","","Conciliado"),
        ("2026-03-16","Otro Movimiento de Retiro","29590749","cargo",493849.32,"","","","","","Pendiente"),
        ("2026-03-16","GMF","11813829","cargo",1975.40,"Impuestos no acreditables","54100501","","Global66","GMF retiro 29590749","Conciliado"),
        ("2026-03-16","IMPUESTO IVA","11813830","cargo",420.28,"IVA descontable","51157001","","Global66","IVA cobro retiro 16/03","Conciliado"),
        ("2026-03-16","COBRO POR RETIRO","11813832","cargo",2212.00,"Comisiones bancarias","53051501","","Global66","Comisión retiro 16/03","Conciliado"),
        ("2026-03-17","Otro Movimiento de Retiro","29649567","cargo",109900.00,"","","","","","Pendiente"),
        ("2026-03-17","GMF","11842042","cargo",439.60,"Impuestos no acreditables","54100501","","Global66","GMF retiro 29649567","Conciliado"),
        ("2026-03-17","Otro Movimiento de Retiro","29659075","cargo",501864.00,"","","","","","Pendiente"),
        ("2026-03-17","GMF","11846469","cargo",2007.46,"Impuestos no acreditables","54100501","","Global66","GMF retiro 29659075","Conciliado"),
        ("2026-03-18","Otro Movimiento de Retiro","29706076","cargo",588180.23,"","","","","","Pendiente"),
        ("2026-03-18","GMF","11867230","cargo",2352.73,"Impuestos no acreditables","54100501","","Global66","GMF retiro 29706076","Conciliado"),
        ("2026-03-18","IMPUESTO IVA","11867231","cargo",421.04,"IVA descontable","51157001","","Global66","IVA cobro retiro 18/03","Conciliado"),
        ("2026-03-18","COBRO POR RETIRO","11867232","cargo",2216.00,"Comisiones bancarias","53051501","","Global66","Comisión retiro 18/03","Conciliado"),
        ("2026-03-18","Otro Movimiento de Retiro","29720162","cargo",3452466.33,"","","","","","Pendiente"),
        ("2026-03-18","GMF","11873622","cargo",13809.87,"Impuestos no acreditables","54100501","","Global66","GMF retiro 29720162","Conciliado"),
        ("2026-03-18","IMPUESTO IVA","11873623","cargo",421.80,"IVA descontable","51157001","","Global66","IVA cobro retiro grande 18/03","Conciliado"),
        ("2026-03-18","COBRO POR RETIRO","11873624","cargo",2220.00,"Comisiones bancarias","53051501","","Global66","Comisión retiro grande 18/03","Conciliado"),
        ("2026-03-19","Otro Movimiento de Retiro","7147213","cargo",15000.00,"","","","","","Pendiente"),
        ("2026-03-19","GMF","11886069","cargo",60.00,"Impuestos no acreditables","54100501","","Global66","GMF retiro 7147213","Conciliado"),
        ("2026-03-19","Otro Movimiento de Retiro","29748521","cargo",1032658.00,"","","","","","Pendiente"),
        ("2026-03-19","GMF","11886072","cargo",4130.64,"Impuestos no acreditables","54100501","","Global66","GMF retiro 29748521","Conciliado"),
        ("2026-03-19","IMPUESTO IVA","11886074","cargo",420.28,"IVA descontable","51157001","","Global66","IVA cobro retiro 19/03","Conciliado"),
        ("2026-03-19","COBRO POR RETIRO","11886075","cargo",2212.00,"Comisiones bancarias","53051501","","Global66","Comisión retiro 19/03","Conciliado"),
        ("2026-03-19","Otro Movimiento de Retiro","7155953","cargo",1000000.00,"","","","","","Pendiente"),
        ("2026-03-19","GMF","11899106","cargo",4000.00,"Impuestos no acreditables","54100501","","Global66","GMF retiro 7155953","Conciliado"),
        ("2026-03-20","Otro Movimiento de Depósito","65393","abono",21922329.62,"","","13050501 / 23550001","","","Pendiente"),
        ("2026-03-30","Otro Movimiento de Retiro","30259280","cargo",3480000.00,"","","","","","Pendiente"),
        ("2026-03-30","Otro Movimiento de Retiro","30259281","cargo",1059927.00,"","","","","","Pendiente"),
        ("2026-03-30","Otro Movimiento de Retiro","7324627","cargo",859927.00,"","","","","","Pendiente"),
        ("2026-03-30","GMF","12135988","cargo",13920.00,"Impuestos no acreditables","54100501","","Global66","GMF retiros 30/03 bloque 1","Conciliado"),
        ("2026-03-30","Otro Movimiento de Retiro","7324628","cargo",3469095.00,"","","","","","Pendiente"),
        ("2026-03-30","GMF + IVA + COBRO POR RETIRO","12135990-12135996","cargo",46594.56,"GMF / IVA / Comision","54100501 / 51157001 / 53051501","","Global66","Impuestos y comisiones bloque 30/03","Conciliado"),
        ("2026-03-30","Otro Movimiento de Retiro","7324629","cargo",959927.00,"","","","","","Pendiente"),
        ("2026-03-30","GMF","12136000","cargo",3839.71,"Impuestos no acreditables","54100501","","Global66","GMF retiro 7324629","Conciliado"),
        ("2026-03-30","Otro Movimiento de Retiro (x3)","30259284 / 30259282 / 30259283","cargo",11694927.00,"","","","","Retiros $3,955,000+$1,859,927+$5,880,000","Pendiente"),
        ("2026-03-30","GMF + IVA + COBRO cierre","12136003-12136013","cargo",68856.56,"GMF / IVA / Comision","54100501 / 51157001 / 53051501","","Global66","Impuestos y comisiones cierre 30/03","Conciliado"),
        ("2026-03-31","Intereses del periodo","-","abono",45460.74,"Intereses","42100501","Financieros / Intereses","Global66","Rendimientos cuenta ahorro mar-2026","Conciliado"),
    ]
    return [make_tx(*r, tx_id=1001 + i) for i, r in enumerate(rows)]


def _default_data() -> dict:
    return {
        "version": "1.0",
        "currentPeriodId": "2026-03",
        "alegra": {"email": "", "token": "", "bank_account_id": None},
        "periods": {
            "2026-03": {
                "id": "2026-03",
                "nombre": "Marzo 2026",
                "banco": "Global66 COP",
                "cuenta": "11200502",
                "empresa": "Mercury Methods Ltda",
                "saldoInicial": 11351966.78,
                "transactions": _marzo_2026_txs(),
            }
        },
    }


# ── PERSISTENCIA ─────────────────────────────────────────────────────────
def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            mx = max(
                (t.get("id", 0) for p in data["periods"].values() for t in p["transactions"]),
                default=1000,
            )
            st.session_state["_id_ctr"] = mx
            return data
        except Exception:
            pass
    return _default_data()


def save_data(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── HELPERS ───────────────────────────────────────────────────────────────
def fmt(n) -> str:
    try:
        return f"${float(n):,.2f}"
    except Exception:
        return "–"


def cur_per(data: dict):
    return data["periods"].get(data["currentPeriodId"])


def totals(txs: list):
    c = sum(t["monto"] for t in txs if t["tipo"] == "cargo")
    a = sum(t["monto"] for t in txs if t["tipo"] == "abono")
    return c, a


def period_range(per: dict):
    pid = per["id"]
    y, m = int(pid[:4]), int(pid[5:7])
    last = calendar.monthrange(y, m)[1]
    return f"{pid}-01", f"{pid}-{last:02d}"


def filtered_txs(per: dict) -> list:
    txs = per["transactions"]
    mode  = st.session_state.get("filter_mode", "month")
    fdate = st.session_state.get("filter_date", "")
    bwm   = st.session_state.get("bw_month", "")
    bwh   = st.session_state.get("bw_half", 1)
    if mode == "month":
        return txs
    if mode == "day":
        return [t for t in txs if t["fecha"] == fdate]
    if mode == "week" and fdate:
        d   = datetime.strptime(fdate, "%Y-%m-%d")
        mon = d - timedelta(days=d.weekday())
        sun = mon + timedelta(days=6)
        return [t for t in txs if mon.date() <= datetime.strptime(t["fecha"], "%Y-%m-%d").date() <= sun.date()]
    if mode == "biweek" and bwm:
        return [t for t in txs if t["fecha"].startswith(bwm) and
                (int(t["fecha"][8:10]) <= 15 if bwh == 1 else int(t["fecha"][8:10]) > 15)]
    return txs


# ── INIT SESSION STATE ────────────────────────────────────────────────────
def _init():
    if "data"            not in st.session_state: st.session_state.data            = load_data()
    if "filter_mode"     not in st.session_state: st.session_state.filter_mode     = "month"
    if "filter_date"     not in st.session_state: st.session_state.filter_date     = date.today().isoformat()
    if "bw_month"        not in st.session_state: st.session_state.bw_month        = ""
    if "bw_half"         not in st.session_state: st.session_state.bw_half         = 1
    if "dialog"          not in st.session_state: st.session_state.dialog          = None
    if "edit_tx_id"      not in st.session_state: st.session_state.edit_tx_id      = None
    if "al_contacts"     not in st.session_state: st.session_state.al_contacts     = []
    if "al_accounts"     not in st.session_state: st.session_state.al_accounts     = []
    if "al_bank_accounts"not in st.session_state: st.session_state.al_bank_accounts= []
    if "al_txs"          not in st.session_state: st.session_state.al_txs          = []


# ── ALEGRA ────────────────────────────────────────────────────────────────
def _alegra_client():
    cfg = st.session_state.data.get("alegra", {})
    # Prioridad: st.secrets (Streamlit Cloud) > configuración guardada en UI
    try:
        sec = st.secrets.get("alegra", {})
        email = sec.get("email", "").strip() or cfg.get("email", "").strip()
        token = sec.get("token", "").strip() or cfg.get("token", "").strip()
    except Exception:
        email = cfg.get("email", "").strip()
        token = cfg.get("token", "").strip()
    if not (email and token):
        return None
    try:
        from alegra_client import AlegraClient
        return AlegraClient(email, token)
    except Exception:
        return None


def _refresh_catalogs():
    c = _alegra_client()
    if not c:
        return
    try:
        contacts = c.get_contacts()
        st.session_state.al_contacts = [x.get("name","") for x in contacts if x.get("name")]
    except Exception:
        pass
    try:
        accounts = c.get_accounts()
        st.session_state.al_accounts = [
            f"{x.get('id','')} – {x.get('name','')}" for x in accounts
        ]
    except Exception:
        pass
    try:
        st.session_state.al_bank_accounts = c.get_bank_accounts()
    except Exception:
        pass


# ── DIÁLOGO: PERÍODO ──────────────────────────────────────────────────────
@st.dialog("Período de conciliación")
def _dlg_period():
    data  = st.session_state.data
    edit  = (st.session_state.dialog == "edit_period")
    per   = cur_per(data) if edit else None

    st.subheader("Editar período" if edit else "Nuevo período")

    nombre = st.text_input("Nombre *", value=per["nombre"] if per else "")
    if edit:
        st.text_input("ID período", value=per["id"], disabled=True)
        pid = per["id"]
    else:
        pid = st.text_input("ID período (YYYY-MM) *", placeholder="2026-04", max_chars=7)

    c1, c2 = st.columns(2)
    with c1:
        if per:
            c_t, a_t = totals(per["transactions"])
            default_si = per["saldoInicial"] - c_t + a_t if edit else per["saldoInicial"]
        else:
            default_si = 0.0
        saldo_ini = st.number_input("Saldo inicial ($)", value=float(per["saldoInicial"]) if per else default_si, step=0.01)
        banco     = st.selectbox("Banco", BANCOS, index=BANCOS.index(per["banco"]) if per and per["banco"] in BANCOS else 0)
    with c2:
        cuenta  = st.text_input("N° Cuenta", value=per.get("cuenta","") if per else "")
        empresa = st.text_input("Empresa",   value=per.get("empresa","Mercury Methods Ltda") if per else "Mercury Methods Ltda")

    ok_col, cancel_col = st.columns(2)
    with cancel_col:
        if st.button("Cancelar", use_container_width=True):
            st.session_state.dialog = None
            st.rerun()
    with ok_col:
        if st.button("Guardar", type="primary", use_container_width=True):
            if not nombre.strip():
                st.error("El nombre es requerido.")
                return
            if not edit:
                if not pid or len(pid) != 7 or pid[4] != "-":
                    st.error("ID inválido. Use formato YYYY-MM (ej: 2026-04).")
                    return
                if pid in data["periods"]:
                    st.error(f"Ya existe un período con ID '{pid}'.")
                    return
                data["periods"][pid] = {
                    "id": pid, "nombre": nombre, "banco": banco,
                    "cuenta": cuenta, "empresa": empresa,
                    "saldoInicial": saldo_ini, "transactions": [],
                }
                data["currentPeriodId"] = pid
            else:
                per.update({"nombre": nombre, "banco": banco,
                            "cuenta": cuenta, "empresa": empresa,
                            "saldoInicial": saldo_ini})
            save_data(data)
            st.session_state.dialog = None
            st.rerun()


# ── DIÁLOGO: TRANSACCIÓN ──────────────────────────────────────────────────
@st.dialog("Movimiento bancario", width="large")  # noqa: E302
def _dlg_tx():
    data    = st.session_state.data
    per     = cur_per(data)
    edit_id = st.session_state.edit_tx_id
    existing = next((t for t in per["transactions"] if t["id"] == edit_id), None) if edit_id is not None else None

    st.subheader("Editar movimiento" if existing else "Agregar movimiento")

    c1, c2 = st.columns(2)
    with c1:
        fecha = st.date_input(
            "Fecha *",
            value=datetime.strptime(existing["fecha"], "%Y-%m-%d").date() if existing else date.today(),
        )
        tipo  = st.selectbox("Tipo *", ["cargo", "abono"],
                              index=0 if not existing or existing["tipo"] == "cargo" else 1)
    with c2:
        monto    = st.number_input("Monto * ($)", min_value=0.01, step=0.01,
                                    value=float(existing["monto"]) if existing else 0.01)
        movim    = st.text_input("N° Movimiento", value=existing.get("movimiento","") if existing else "")

    desc = st.text_input("Descripción extracto *", value=existing.get("descripcion","") if existing else "")

    c3, c4 = st.columns(2)
    with c3:
        concepto   = st.text_input("Concepto Alegra",  value=existing.get("concepto","")   if existing else "")
        cuenta     = st.text_input("Cuenta contable",  value=existing.get("cuenta","")     if existing else "")
        cuenta_ref = st.text_input("Ref. cuenta",      value=existing.get("cuentaRef","")  if existing else "")
    with c4:
        al_contacts = st.session_state.al_contacts
        if al_contacts:
            cur_ct = existing.get("contacto","") if existing else ""
            opts   = ([cur_ct] + al_contacts) if cur_ct and cur_ct not in al_contacts else (al_contacts if al_contacts else [""])
            contacto = st.selectbox("Contacto", opts,
                                     index=opts.index(cur_ct) if cur_ct in opts else 0)
        else:
            contacto = st.text_input("Contacto", value=existing.get("contacto","") if existing else "")
        estado = st.selectbox("Estado", ESTADOS,
                               index=ESTADOS.index(existing["estado"]) if existing and existing["estado"] in ESTADOS else 0)
        nota   = st.text_input("Notas", value=existing.get("nota","") if existing else "")

    ok_col, cancel_col = st.columns(2)
    with cancel_col:
        if st.button("Cancelar", use_container_width=True):
            st.session_state.dialog    = None
            st.session_state.edit_tx_id = None
            st.rerun()
    with ok_col:
        if st.button("Guardar", type="primary", use_container_width=True):
            if not desc.strip():
                st.error("La descripción es requerida.")
                return
            if monto <= 0:
                st.error("El monto debe ser mayor a 0.")
                return
            t = make_tx(fecha.isoformat(), desc, movim, tipo, monto,
                        concepto, cuenta, cuenta_ref, contacto, nota, estado,
                        tx_id=edit_id)
            if existing:
                idx = next(i for i, x in enumerate(per["transactions"]) if x["id"] == edit_id)
                per["transactions"][idx] = t
            else:
                per["transactions"].append(t)
            save_data(data)
            st.session_state.dialog    = None
            st.session_state.edit_tx_id = None
            st.rerun()


# ── DIÁLOGO: CSV ──────────────────────────────────────────────────────────
@st.dialog("Importar extracto bancario (CSV)", width="large")
def _dlg_csv():
    data = st.session_state.data
    per  = cur_per(data)

    st.markdown(
        "**Columnas:** Fecha · Descripción · N°Movimiento · Tipo (cargo/abono) · "
        "Monto · Concepto · CuentaContable · RefCuenta · Contacto · Nota · Estado"
    )
    sep_label = st.radio("Separador", [",", ";", "Tab"], horizontal=True)
    sep = "\t" if sep_label == "Tab" else sep_label

    tab_file, tab_text = st.tabs(["Subir archivo", "Pegar texto"])
    raw = ""
    with tab_file:
        f = st.file_uploader("Archivo CSV / TXT", type=["csv","txt"])
        if f:
            raw = f.read().decode("utf-8", errors="replace")
    with tab_text:
        raw = st.text_area("Contenido CSV", height=150,
                            placeholder="2026-04-01,Retiro nomina,30000000,cargo,5000000") or raw

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Vista previa"):
            if raw.strip():
                lines = [ln.split(sep) for ln in raw.strip().splitlines() if ln.strip()]
                cols  = ["Fecha","Desc","N°Mov","Tipo","Monto","Concepto","Cuenta","RefCta","Contacto","Nota","Estado"]
                n     = min(len(cols), len(lines[0])) if lines else 0
                st.dataframe(pd.DataFrame(lines[:10], columns=cols[:n]), use_container_width=True)
    with c2:
        if st.button("Cancelar"):
            st.session_state.dialog = None
            st.rerun()
    with c3:
        if st.button("Importar", type="primary"):
            if not raw.strip():
                st.error("Sin datos.")
                return
            ok = bad = 0
            for line in raw.strip().splitlines():
                r = [c.strip().strip('"') for c in line.split(sep)]
                try:
                    fecha = r[0]; desc = r[1] if len(r) > 1 else ""
                    if not fecha or not desc:
                        bad += 1; continue
                    monto = float(r[4].replace(",",".")) if len(r) > 4 else 0
                    if monto <= 0:
                        bad += 1; continue
                    tipo_raw = r[3].lower() if len(r) > 3 else "cargo"
                    tipo = "cargo" if any(x in tipo_raw for x in ["cargo","retiro","deb"]) else "abono"
                    per["transactions"].append(make_tx(
                        fecha, desc,
                        r[2] if len(r) > 2 else "",
                        tipo, monto,
                        r[5] if len(r) > 5 else "",
                        r[6] if len(r) > 6 else "",
                        r[7] if len(r) > 7 else "",
                        r[8] if len(r) > 8 else "",
                        r[9] if len(r) > 9 else "",
                        r[10] if len(r) > 10 else "Pendiente",
                    ))
                    ok += 1
                except Exception:
                    bad += 1
            save_data(data)
            st.success(f"{ok} importados" + (f" ({bad} con errores)" if bad else ""))
            st.session_state.dialog = None
            st.rerun()


# ── SIDEBAR ───────────────────────────────────────────────────────────────
def _sidebar():
    data = st.session_state.data
    per  = cur_per(data)

    st.sidebar.markdown("## 🏦 Conciliación Bancaria\n**Mercury Methods Ltda**")
    st.sidebar.divider()

    # ── Período ────────────────────────────────────────────────────────
    st.sidebar.markdown("### 📅 Período")
    periods = sorted(data["periods"].values(), key=lambda p: p["id"], reverse=True)
    ids     = [p["id"] for p in periods]
    labels  = [f"{p['nombre']} — {p['banco']}" for p in periods]
    cur_idx = ids.index(data["currentPeriodId"]) if data["currentPeriodId"] in ids else 0

    new_idx = st.sidebar.selectbox(
        "Período activo", range(len(labels)),
        format_func=lambda i: labels[i], index=cur_idx,
    )
    if ids[new_idx] != data["currentPeriodId"]:
        data["currentPeriodId"] = ids[new_idx]
        save_data(data)
        st.rerun()

    if per:
        st.sidebar.caption(f"{per.get('empresa','')} | Cta: {per.get('cuenta','')}")
        banco_idx = BANCOS.index(per["banco"]) if per["banco"] in BANCOS else 0
        nuevo_banco = st.sidebar.selectbox("Banco", BANCOS, index=banco_idx)
        if nuevo_banco != per["banco"]:
            per["banco"] = nuevo_banco
            save_data(data)
            st.rerun()

    col1, col2 = st.sidebar.columns(2)
    if col1.button("➕ Nuevo",  use_container_width=True):
        st.session_state.dialog = "new_period"
        st.rerun()
    if col2.button("✏️ Editar", use_container_width=True):
        if per:
            st.session_state.dialog = "edit_period"
            st.rerun()

    if per and st.sidebar.button("🗑️ Eliminar período", use_container_width=True):
        if len(data["periods"]) <= 1:
            st.sidebar.error("No se puede eliminar el único período.")
        else:
            st.session_state.dialog = "delete_period"
            st.rerun()

    st.sidebar.divider()

    # ── Alegra ─────────────────────────────────────────────────────────
    st.sidebar.markdown("### 🔗 Alegra")
    cfg = data.setdefault("alegra", {"email": "", "token": "", "bank_account_id": None})
    connected = bool(cfg.get("email") and cfg.get("token"))
    st.sidebar.caption("✅ Conectado" if connected else "⚠️ Sin credenciales")

    with st.sidebar.expander("Configurar", expanded=not connected):
        email = st.text_input("Email Alegra", value=cfg.get("email",""), key="al_email")
        token = st.text_input("Token API",    value=cfg.get("token",""), type="password", key="al_token")
        c1, c2 = st.columns(2)
        if c1.button("Guardar", key="al_save"):
            cfg["email"] = email.strip()
            cfg["token"] = token.strip()
            save_data(data)
            _refresh_catalogs()
            st.success("Guardado")
        if c2.button("Probar", key="al_test"):
            client = _alegra_client()
            if not client:
                st.error("Complete email y token.")
            else:
                try:
                    info = client.test_connection()
                    name = info.get("name") or "OK"
                    st.success(f"✅ {name}")
                    _refresh_catalogs()
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.al_bank_accounts:
        ba_opts = {b.get("name", str(b.get("id",""))): b.get("id")
                   for b in st.session_state.al_bank_accounts}
        ba_names = list(ba_opts.keys())
        cur_id   = cfg.get("bank_account_id")
        cur_name = next((n for n, i in ba_opts.items() if i == cur_id), ba_names[0])
        sel = st.sidebar.selectbox("Cuenta bancaria Alegra", ba_names,
                                    index=ba_names.index(cur_name) if cur_name in ba_names else 0)
        if ba_opts.get(sel) != cur_id:
            cfg["bank_account_id"] = ba_opts.get(sel)
            save_data(data)

    st.sidebar.divider()

    # ── Export / Import ─────────────────────────────────────────────────
    st.sidebar.markdown("### 📂 Datos")
    st.sidebar.download_button(
        "⬇️ Exportar JSON",
        data=json.dumps(data, ensure_ascii=False, indent=2),
        file_name=f"conciliacion_{date.today().isoformat()}.json",
        mime="application/json", use_container_width=True,
    )
    uploaded = st.sidebar.file_uploader("⬆️ Importar JSON", type=["json"])
    if uploaded:
        try:
            imported = json.load(uploaded)
            if "periods" not in imported or "currentPeriodId" not in imported:
                raise ValueError("Formato inválido")
            st.session_state.data = imported
            mx = max((t.get("id",0) for p in imported["periods"].values()
                      for t in p["transactions"]), default=1000)
            st.session_state["_id_ctr"] = mx
            save_data(imported)
            st.sidebar.success("Importado correctamente.")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error: {e}")


# ── MÉTRICAS ──────────────────────────────────────────────────────────────
def _metrics(per: dict):
    all_txs = per["transactions"]
    c, a    = totals(all_txs)
    sf      = per["saldoInicial"] - c + a
    conc    = sum(1 for t in all_txs if t["estado"] == "Conciliado")
    pend    = sum(1 for t in all_txs if t["estado"] == "Pendiente")
    rev     = sum(1 for t in all_txs if t["estado"] == "En revisión")
    cols    = st.columns(7)
    labels  = ["Saldo inicial","Total cargos","Total abonos","Saldo final",
               "Movimientos","Conciliados","Pendientes"]
    values  = [fmt(per["saldoInicial"]), fmt(c), fmt(a), fmt(sf),
               len(all_txs), conc, pend]
    deltas  = [None, f"-{fmt(c)}", fmt(a), None, None, None,
               f"+{rev} en rev." if rev else None]
    delta_c = ["normal","inverse","normal","normal","normal","normal","inverse"]
    for col, lbl, val, dlt, dc in zip(cols, labels, values, deltas, delta_c):
        with col:
            st.metric(lbl, val, delta=dlt, delta_color=dc)


# ── FILTROS ───────────────────────────────────────────────────────────────
def _filters(per: dict):
    c1, c2, c3 = st.columns([4, 4, 3])
    with c1:
        mode = st.radio("Ver por", ["Mes completo","Semana","Quincena","Día"],
                         horizontal=True, key="filter_radio_r")
        st.session_state.filter_mode = {
            "Mes completo":"month","Semana":"week",
            "Quincena":"biweek","Día":"day"
        }[mode]
    with c2:
        m = st.session_state.filter_mode
        if m == "day":
            d = st.date_input("Fecha", key="fd_day_i")
            st.session_state.filter_date = d.isoformat()
        elif m == "week":
            d = st.date_input("Fecha en la semana", key="fd_week_i")
            st.session_state.filter_date = d.isoformat()
            mon = d - timedelta(days=d.weekday())
            sun = mon + timedelta(days=6)
            st.caption(f"Semana: {mon.strftime('%d/%m')} – {sun.strftime('%d/%m/%Y')}")
        elif m == "biweek":
            months = sorted({t["fecha"][:7] for t in per["transactions"]})
            mlabels = {ms: datetime(int(ms[:4]),int(ms[5:7]),1).strftime("%B %Y").capitalize()
                       for ms in months}
            if months:
                sel_m = st.selectbox("Mes", months, format_func=lambda m: mlabels.get(m,m),
                                      key="bw_month_i")
                st.session_state.bw_month = sel_m
            st.session_state.bw_half = st.radio(
                "Quincena", [1, 2],
                format_func=lambda h: "1ª (1–15)" if h == 1 else "2ª (16–fin)",
                horizontal=True, key="bw_half_i",
            )
    with c3:
        filt = filtered_txs(per)
        fc, fa = totals(filt)
        st.caption(
            f"**{len(filt)}** movimientos\n\n"
            f"Cargos: **{fmt(fc)}**  Abonos: **{fmt(fa)}**"
        )


# ── TABLA PRINCIPAL ───────────────────────────────────────────────────────
def _table(per: dict):
    data = st.session_state.data
    txs  = sorted(filtered_txs(per), key=lambda t: (t["fecha"], t["id"]))

    if not txs:
        st.info("Sin movimientos en este filtro.")
        return

    df = pd.DataFrame(txs)
    df["Cargo ($)"] = df.apply(lambda r: r["monto"] if r["tipo"] == "cargo" else None, axis=1)
    df["Abono ($)"] = df.apply(lambda r: r["monto"] if r["tipo"] == "abono" else None, axis=1)

    display_cols = ["id","fecha","descripcion","movimiento","tipo",
                    "Cargo ($)","Abono ($)","concepto","cuenta","cuentaRef",
                    "contacto","nota","estado"]
    df_view = df[display_cols].copy()

    al_contacts = st.session_state.al_contacts or \
                  sorted({t.get("contacto","") for t in per["transactions"]} - {""})
    al_accounts = st.session_state.al_accounts or \
                  sorted({t.get("cuenta","") for t in per["transactions"]} - {""})

    edited = st.data_editor(
        df_view,
        column_config={
            "id":          None,
            "fecha":       st.column_config.TextColumn("Fecha",      disabled=True),
            "descripcion": st.column_config.TextColumn("Descripción",disabled=True, width="large"),
            "movimiento":  st.column_config.TextColumn("N° Mov.",    disabled=True),
            "tipo":        st.column_config.SelectboxColumn("Tipo",  options=["cargo","abono"], disabled=True, width="small"),
            "Cargo ($)":   st.column_config.NumberColumn("Cargo ($)",disabled=True, format="$%,.2f"),
            "Abono ($)":   st.column_config.NumberColumn("Abono ($)",disabled=True, format="$%,.2f"),
            "concepto":    st.column_config.TextColumn("Concepto Alegra"),
            "cuenta":      st.column_config.SelectboxColumn("Cuenta contable", options=al_accounts) if al_accounts
                           else st.column_config.TextColumn("Cuenta contable"),
            "cuentaRef":   st.column_config.TextColumn("Ref. cuenta"),
            "contacto":    st.column_config.SelectboxColumn("Contacto", options=al_contacts) if al_contacts
                           else st.column_config.TextColumn("Contacto"),
            "nota":        st.column_config.TextColumn("Notas"),
            "estado":      st.column_config.SelectboxColumn("Estado", options=ESTADOS, width="medium"),
        },
        disabled=["fecha","descripcion","movimiento","tipo","Cargo ($)","Abono ($)"],
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key="tx_table",
    )

    # Aplicar edits inline (concepto, cuenta, contacto, nota, estado)
    editable = ["concepto","cuenta","cuentaRef","contacto","nota","estado"]
    id_map   = {t["id"]: t for t in per["transactions"]}
    changed  = False
    for i, row in edited.iterrows():
        tid = df_view.iloc[i]["id"]
        t   = id_map.get(tid)
        if t is None:
            continue
        for f in editable:
            nv = row[f] if row[f] is not None else ""
            if str(t.get(f,"")) != str(nv):
                t[f] = nv
                changed = True
    if changed:
        save_data(data)

    fc, fa = totals(txs)
    sf_all = per["saldoInicial"] - totals(per["transactions"])[0] + totals(per["transactions"])[1]
    st.markdown(
        f"**TOTALES ({len(txs)} mov.)** &nbsp;│&nbsp; "
        f"Cargos: **{fmt(fc)}** &nbsp;│&nbsp; Abonos: **{fmt(fa)}** &nbsp;│&nbsp; "
        f"Saldo calculado: **{fmt(sf_all)}**"
    )


# ── PANEL ALEGRA ──────────────────────────────────────────────────────────
def _alegra_panel(per: dict):
    data   = st.session_state.data
    client = _alegra_client()
    if not client:
        st.info("Configure las credenciales de Alegra en el panel lateral para sincronizar.")
        return

    date_start, date_end = period_range(per)
    ba_id = data.get("alegra",{}).get("bank_account_id")

    c1, c2, c3 = st.columns([3, 3, 2])
    with c1:
        st.caption(f"Período: **{date_start}** → **{date_end}**")
    with c2:
        if ba_id and st.session_state.al_bank_accounts:
            ba_name = next(
                (b.get("name","") for b in st.session_state.al_bank_accounts if b.get("id") == ba_id),
                str(ba_id),
            )
            st.caption(f"Cuenta Alegra: **{ba_name}**")
    with c3:
        if st.button("🔄 Sincronizar desde Alegra", type="primary"):
            with st.spinner("Consultando Alegra..."):
                al_txs = []
                try:
                    for p in client.get_payments(date_start, date_end, ba_id):
                        amt = float(p.get("amount",0))
                        if amt > 0:
                            al_txs.append({
                                "fecha":       (p.get("date","") or "")[:10],
                                "descripcion": p.get("observations") or "Pago recibido",
                                "movimiento":  str(p.get("id","")),
                                "tipo":        "abono",
                                "monto":       amt,
                                "concepto":    "",
                                "cuenta":      "",
                                "cuentaRef":   "",
                                "contacto":    (p.get("contact") or {}).get("name",""),
                                "nota":        f"Alegra #{p.get('id','')}",
                                "estado":      "Pendiente",
                            })
                except Exception as e:
                    st.warning(f"Pagos: {e}")
                try:
                    for b in client.get_bills(date_start, date_end):
                        amt = float(b.get("amount",0))
                        if amt > 0:
                            al_txs.append({
                                "fecha":       (b.get("date","") or "")[:10],
                                "descripcion": b.get("observations") or "Compra/Gasto",
                                "movimiento":  str(b.get("id","")),
                                "tipo":        "cargo",
                                "monto":       amt,
                                "concepto":    "",
                                "cuenta":      "",
                                "cuentaRef":   "",
                                "contacto":    (b.get("provider") or {}).get("name",""),
                                "nota":        f"Alegra #{b.get('id','')}",
                                "estado":      "Pendiente",
                            })
                except Exception as e:
                    st.warning(f"Compras: {e}")
                st.session_state.al_txs = al_txs

    al_txs = st.session_state.al_txs
    if not al_txs:
        st.info("Haga clic en 'Sincronizar' para traer movimientos desde Alegra.")
        return

    st.markdown(f"**{len(al_txs)}** registros encontrados en Alegra:")
    df_al = pd.DataFrame(al_txs)
    df_al["Cargo ($)"] = df_al.apply(lambda r: r["monto"] if r["tipo"]=="cargo" else None, axis=1)
    df_al["Abono ($)"] = df_al.apply(lambda r: r["monto"] if r["tipo"]=="abono" else None, axis=1)
    st.dataframe(
        df_al[["fecha","descripcion","movimiento","Cargo ($)","Abono ($)","contacto","nota"]],
        use_container_width=True, hide_index=True,
        column_config={
            "Cargo ($)": st.column_config.NumberColumn(format="$%,.2f"),
            "Abono ($)": st.column_config.NumberColumn(format="$%,.2f"),
        },
    )

    existing_movs = {t["movimiento"] for t in per["transactions"]}
    nuevos = [t for t in al_txs if t["movimiento"] not in existing_movs]
    if nuevos:
        st.info(f"🆕 **{len(nuevos)}** registros nuevos (aún no están en la conciliación).")
        if st.button(f"➕ Importar {len(nuevos)} movimientos nuevos de Alegra", type="primary"):
            for t in nuevos:
                per["transactions"].append(make_tx(**t))
            save_data(data)
            st.session_state.al_txs = []
            st.success(f"✅ {len(nuevos)} movimientos importados.")
            st.rerun()
    else:
        st.success("✅ Todos los registros de Alegra ya están en la conciliación.")


# ── MAIN ──────────────────────────────────────────────────────────────────
def main():
    _init()
    _sidebar()

    data = st.session_state.data
    per  = cur_per(data)

    # ── Diálogos activos ──────────────────────────────────────────────
    dlg = st.session_state.dialog
    if dlg in ("new_period","edit_period"):
        _dlg_period()
    elif dlg == "tx":
        if per:
            _dlg_tx()
    elif dlg == "csv":
        if per:
            _dlg_csv()
    elif dlg == "delete_period":
        # Confirmación inline (no usa st.dialog para que sea más directo)
        st.warning(
            f"¿Eliminar el período **{per['nombre']}**? Esta acción no se puede deshacer.",
            icon="⚠️",
        )
        c1, c2, _ = st.columns([1,1,4])
        if c1.button("Sí, eliminar", type="primary"):
            del data["periods"][data["currentPeriodId"]]
            data["currentPeriodId"] = list(data["periods"].keys())[0]
            save_data(data)
            st.session_state.dialog = None
            st.rerun()
        if c2.button("Cancelar"):
            st.session_state.dialog = None
            st.rerun()
        return  # No renderizar el resto mientras se confirma

    if not per:
        st.error("No hay períodos. Cree uno en el panel lateral.")
        return

    # ── Header ────────────────────────────────────────────────────────
    st.markdown(
        f"""<div style="background:#2c3e50;color:#fff;padding:12px 20px;border-radius:8px;
            margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;">
            <div>
                <strong style="font-size:1.1rem;">Conciliación Bancaria</strong>
                <span style="font-size:.8rem;opacity:.7;margin-left:12px;">
                    {per.get('empresa','')} — {per.get('banco','')}
                </span>
            </div>
            <div style="font-size:.8rem;opacity:.7;">{per.get('nombre','')} | Cta: {per.get('cuenta','')}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── Métricas ──────────────────────────────────────────────────────
    _metrics(per)
    st.markdown("")

    # ── Filtros ───────────────────────────────────────────────────────
    with st.expander("🔎 Filtros", expanded=True):
        _filters(per)

    # ── Acciones ──────────────────────────────────────────────────────
    a1, a2, a3, a4, _ = st.columns([1.4, 1.4, 1.2, 1.2, 4])
    with a1:
        if st.button("➕ Agregar movimiento", use_container_width=True, type="primary"):
            st.session_state.dialog    = "tx"
            st.session_state.edit_tx_id = None
            st.rerun()
    with a2:
        if st.button("📋 Importar CSV", use_container_width=True):
            st.session_state.dialog = "csv"
            st.rerun()
    with a3:
        if st.button("💾 Guardar", use_container_width=True):
            save_data(data)
            st.toast("Guardado ✅")
    with a4:
        if st.button("🔄 Catálogos Alegra", use_container_width=True):
            _refresh_catalogs()
            st.toast("Catálogos actualizados")

    st.markdown("")

    # ── Tabs ─────────────────────────────────────────────────────────
    tab_mov, tab_alegra = st.tabs(["📊 Movimientos", "🔗 Sincronización Alegra"])

    with tab_mov:
        _table(per)
        st.divider()
        st.markdown("**Editar o eliminar un movimiento:**")
        txs_sorted = sorted(per["transactions"], key=lambda t: (t["fecha"], t["id"]))
        if txs_sorted:
            lbl = {t["id"]: f"{t['fecha']}  |  {t['descripcion'][:45]}  |  {fmt(t['monto'])} ({t['tipo']})"
                   for t in txs_sorted}
            sel = st.selectbox("Seleccione", list(lbl.keys()), format_func=lambda i: lbl[i],
                                label_visibility="collapsed")
            b1, b2, _ = st.columns([1,1,6])
            if b1.button("✏️ Editar", key="row_edit"):
                st.session_state.dialog    = "tx"
                st.session_state.edit_tx_id = sel
                st.rerun()
            if b2.button("🗑️ Eliminar", key="row_del"):
                per["transactions"] = [t for t in per["transactions"] if t["id"] != sel]
                save_data(data)
                st.toast("Movimiento eliminado 🗑️")
                st.rerun()

    with tab_alegra:
        _alegra_panel(per)


if __name__ == "__main__":
    main()
