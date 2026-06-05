"""Conciliación Bancaria – Mercury Methods v2.0
Multi-empresa · Multi-período · Autenticación · Import/Export
"""

import io
import json
import calendar
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st
import auth as _auth

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Conciliación Bancaria – Mercury Methods",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
_local = Path(__file__).parent / "conciliacion_data.json"
try:
    _local.touch(exist_ok=True)
    DATA_FILE = _local
except (PermissionError, OSError):
    DATA_FILE = Path("/tmp") / "conciliacion_data.json"

BANCOS  = ["Global66 COP", "Global66 USD", "Davivienda", "Bancolombia", "Nequi"]
ESTADOS = ["Pendiente", "Conciliado", "En revisión"]

COMPANIES = [
    {"id": "mercury-ltda",  "name": "Mercury Methods LTDA"},
    {"id": "mercury-llc",   "name": "Mercury Methods LLC"},
    {"id": "david-illidge", "name": "David Illidge"},
    {"id": "azahar-retail", "name": "Azahar Retail"},
    {"id": "test",          "name": "TEST"},
]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Ocultar barra superior Streamlit */
header[data-testid="stHeader"]  { display:none !important; }
[data-testid="stToolbar"]       { display:none !important; }
[data-testid="stDecoration"]    { display:none !important; }
.stDeployButton                 { display:none !important; }
#MainMenu                       { display:none !important; }
footer                          { display:none !important; }

/* Métricas */
div[data-testid="metric-container"] {
    background:#fff;border:1px solid #e0e0e0;border-radius:8px;
    padding:10px 14px;box-shadow:0 2px 8px rgba(0,0,0,.08);
}
[data-testid="stMetricLabel"] {font-size:.72rem;color:#757575;}
[data-testid="stMetricValue"] {font-size:1rem;font-weight:700;}
.block-container {padding-top:.6rem !important;}

/* Empresa activa en sidebar */
div[data-testid="stSidebar"] .company-btn-active > button {
    background:#2c3e50 !important;color:#fff !important;font-weight:700 !important;
}

/* Auth card */
.auth-header {
    background:#2c3e50;color:#fff;padding:28px;border-radius:12px 12px 0 0;text-align:center;
}
</style>
""", unsafe_allow_html=True)

# ── NEXT ID ───────────────────────────────────────────────────────────────────
def _nid() -> int:
    st.session_state.setdefault("_id", 1000)
    st.session_state["_id"] += 1
    return st.session_state["_id"]

# ── MAKE TX ───────────────────────────────────────────────────────────────────
def make_tx(fecha="", desc="", mov="", tipo="cargo", monto=0.0,
            concepto="", cuenta="", cuenta_ref="", origen="",
            nota="", estado="Pendiente", tx_id=None) -> dict:
    return {
        "id":          tx_id or _nid(),
        "fecha":       str(fecha),
        "descripcion": str(desc),
        "movimiento":  str(mov),
        "tipo":        tipo,
        "monto":       float(monto),
        "concepto":    concepto,
        "cuenta":      cuenta,
        "cuentaRef":   cuenta_ref,
        "origen":      origen,
        "nota":        nota,
        "estado":      estado,
    }

# ── TEST DATA ─────────────────────────────────────────────────────────────────
def _test_txs() -> list:
    rows = [
        # Enero 2026
        ("2026-01-02","Pago nómina enero 2026","NOM-2601","cargo",8500000,"Nómina","51050501","Gastos de personal / Nómina","Empleados TEST","Nómina mensual enero","Conciliado"),
        ("2026-01-02","GMF 4x1000 nómina enero","GMF-2601","cargo",34000,"Impuestos no acreditables","54100501","Gravamen movimientos financieros","Bancolombia","GMF retiro nómina","Conciliado"),
        ("2026-01-05","Ingreso cliente A - factura 001","ING-001","abono",12500000,"Ventas servicios","41050101","Ingresos por servicios","Cliente A SAS","Pago factura FV-001","Conciliado"),
        ("2026-01-10","Pago arriendo oficina enero","ARR-001","cargo",3200000,"Arrendamientos","52040501","Gastos administrativos / Arriendo","Inmobiliaria XYZ","Arriendo piso 3","Conciliado"),
        ("2026-01-15","Pago servicios públicos","SVC-001","cargo",580000,"Servicios públicos","52040201","Agua, luz, gas","EPM","Servicios enero","Conciliado"),
        ("2026-01-20","Comisión bancaria enero","COM-001","cargo",45000,"Comisiones bancarias","53051501","Comisiones y gastos bancarios","Bancolombia","Cuota mantenimiento cuenta","Conciliado"),
        ("2026-01-25","Ingreso cliente B - factura 002","ING-002","abono",8750000,"Ventas servicios","41050101","Ingresos por servicios","Cliente B LTDA","Pago factura FV-002","Conciliado"),
        ("2026-01-31","Intereses cuenta ahorro enero","INT-001","abono",18500,"Intereses financieros","42100501","Financieros / Intereses","Bancolombia","Rendimientos enero","Conciliado"),
        # Febrero 2026
        ("2026-02-03","Pago nómina febrero 2026","NOM-2602","cargo",8500000,"Nómina","51050501","Gastos de personal / Nómina","Empleados TEST","Nómina mensual febrero","Conciliado"),
        ("2026-02-03","GMF 4x1000 nómina febrero","GMF-2602","cargo",34000,"Impuestos no acreditables","54100501","Gravamen movimientos financieros","Bancolombia","GMF retiro nómina","Conciliado"),
        ("2026-02-10","Pago proveedor tecnología","PRV-001","cargo",2800000,"Servicios de tecnología","51959501","Servicios online / Software","Proveedor Tech SAS","Licencias software feb","Conciliado"),
        ("2026-02-14","Ingreso cliente C - factura 003","ING-003","abono",15000000,"Ventas servicios","41050101","Ingresos por servicios","Cliente C Corp","Pago factura FV-003","Conciliado"),
        ("2026-02-20","Pago IVA bimestre ene-feb","IVA-001","cargo",1850000,"IVA por pagar","24080501","Obligaciones fiscales / IVA","DIAN","Declaración IVA bimestral","Conciliado"),
        ("2026-02-28","Intereses cuenta ahorro febrero","INT-002","abono",19200,"Intereses financieros","42100501","Financieros / Intereses","Bancolombia","Rendimientos febrero","Conciliado"),
        # Marzo 2026
        ("2026-03-03","Pago nómina marzo 2026","NOM-2603","cargo",8500000,"Nómina","51050501","Gastos de personal / Nómina","Empleados TEST","Nómina mensual marzo","Conciliado"),
        ("2026-03-03","GMF 4x1000 nómina marzo","GMF-2603","cargo",34000,"Impuestos no acreditables","54100501","Gravamen movimientos financieros","Bancolombia","GMF retiro nómina","Conciliado"),
        ("2026-03-07","Ingreso cliente A - factura 004","ING-004","abono",13200000,"Ventas servicios","41050101","Ingresos por servicios","Cliente A SAS","Pago factura FV-004","Conciliado"),
        ("2026-03-12","Pago publicidad digital","PUB-001","cargo",950000,"Publicidad y marketing","52900101","Gastos de ventas / Publicidad","Meta Ads","Pauta redes sociales","Pendiente"),
        ("2026-03-15","Pago seguridad social","SEG-001","cargo",1250000,"Seguridad social","51050901","Aportes sociales","ADRES / AFP","Aportes marzo","Conciliado"),
        ("2026-03-20","Devolución cliente B","DEV-001","cargo",500000,"Devoluciones en ventas","41059901","Notas crédito clientes","Cliente B LTDA","NC-001 ajuste factura","Pendiente"),
        ("2026-03-25","Ingreso proyecto especial","ING-005","abono",25000000,"Ventas servicios","41050101","Ingresos por servicios","Cliente D Internacional","Proyecto alpha fase 1","Pendiente"),
        ("2026-03-31","Intereses cuenta ahorro marzo","INT-003","abono",21000,"Intereses financieros","42100501","Financieros / Intereses","Bancolombia","Rendimientos marzo","Conciliado"),
        # Abril 2026
        ("2026-04-02","Pago nómina abril 2026","NOM-2604","cargo",8750000,"Nómina","51050501","Gastos de personal / Nómina","Empleados TEST","Nómina mensual abril + ajuste","Pendiente"),
        ("2026-04-02","GMF 4x1000 nómina abril","GMF-2604","cargo",35000,"Impuestos no acreditables","54100501","Gravamen movimientos financieros","Bancolombia","GMF retiro nómina","Pendiente"),
        ("2026-04-08","Pago arrendamiento oficina abril","ARR-002","cargo",3200000,"Arrendamientos","52040501","Gastos administrativos / Arriendo","Inmobiliaria XYZ","Arriendo piso 3","Pendiente"),
        ("2026-04-15","Ingreso cliente E - factura 005","ING-006","abono",9800000,"Ventas servicios","41050101","Ingresos por servicios","Cliente E SAS","Pago factura FV-005","Pendiente"),
        ("2026-04-20","Renovación dominio y hosting","TEC-001","cargo",320000,"Servicios de tecnología","51959501","Servicios online / Hosting","GoDaddy Colombia","Dominio anual + hosting","Pendiente"),
        # Mayo 2026
        ("2026-05-02","Pago nómina mayo 2026","NOM-2605","cargo",8750000,"Nómina","51050501","Gastos de personal / Nómina","Empleados TEST","Nómina mensual mayo","Pendiente"),
        ("2026-05-02","GMF 4x1000 nómina mayo","GMF-2605","cargo",35000,"Impuestos no acreditables","54100501","Gravamen movimientos financieros","Bancolombia","GMF retiro nómina","Pendiente"),
        ("2026-05-10","Ingreso cliente A - factura 006","ING-007","abono",14500000,"Ventas servicios","41050101","Ingresos por servicios","Cliente A SAS","Pago factura FV-006","Pendiente"),
        ("2026-05-20","Pago IVA bimestre mar-abr","IVA-002","cargo",2100000,"IVA por pagar","24080501","Obligaciones fiscales / IVA","DIAN","Declaración IVA bimestral","Pendiente"),
        # Junio 2026
        ("2026-06-02","Pago nómina junio 2026","NOM-2606","cargo",8750000,"Nómina","51050501","Gastos de personal / Nómina","Empleados TEST","Nómina mensual junio","Pendiente"),
        ("2026-06-02","GMF 4x1000 nómina junio","GMF-2606","cargo",35000,"Impuestos no acreditables","54100501","Gravamen movimientos financieros","Bancolombia","GMF retiro nómina","Pendiente"),
        ("2026-06-04","Ingreso cliente B - factura 007","ING-008","abono",11200000,"Ventas servicios","41050101","Ingresos por servicios","Cliente B LTDA","Pago factura FV-007","Pendiente"),
    ]
    return [make_tx(*r, tx_id=2001+i) for i, r in enumerate(rows)]

# ── DEFAULT DATA ──────────────────────────────────────────────────────────────
def _march_2026_txs() -> list:
    rows = [
        ("2026-03-03","Otro Movimiento de Retiro","28831783","cargo",6405200,"","Según destinatario","22xx","","","Pendiente"),
        ("2026-03-03","GMF","11383614","cargo",12003.56,"Impuestos no acreditables","54100501","GMF 4x1000","Global66","GMF retiro 28831783","Conciliado"),
        ("2026-03-03","Otro Movimiento de Depósito","62012","abono",18795319.37,"","","13050501","","","Pendiente"),
        ("2026-03-05","Compra Comcel Domiciliacion M","11160098","cargo",276080,"Teléfono","51353501","Servicios / Teléfono","Comcel / Claro","","Conciliado"),
        ("2026-03-05","Otro Movimiento de Depósito","28992772","abono",42143.91,"","","13050501","","","Pendiente"),
        ("2026-03-06","Compra Microsoft#g143376191","11192582","cargo",56563.15,"Software contables","51959501","Servicios online / Software","Microsoft","","Conciliado"),
        ("2026-03-06","GMF","11519323","cargo",226.26,"Impuestos no acreditables","54100501","GMF Microsoft","Global66","GMF Microsoft","Conciliado"),
        ("2026-03-13","Compra Comcel Domiciliacion M","11353946","cargo",46472,"Teléfono","51353501","Servicios / Teléfono","Comcel / Claro","","Conciliado"),
        ("2026-03-13","Otro Movimiento de Retiro","7050429","cargo",800000,"","","22xx","","","Pendiente"),
        ("2026-03-15","Compra Movistar Pagosepayco","11413473","cargo",190992,"Teléfono","51353501","Servicios / Teléfono","Movistar Colombia","","Conciliado"),
        ("2026-03-18","Otro Movimiento de Retiro","29720162","cargo",3452466.33,"","","","","","Pendiente"),
        ("2026-03-20","Otro Movimiento de Depósito","65393","abono",21922329.62,"","","13050501","","","Pendiente"),
        ("2026-03-31","Intereses del período","–","abono",45460.74,"Intereses","42100501","Financieros / Intereses","Global66","Rendimientos mar-2026","Conciliado"),
    ]
    return [make_tx(*r, tx_id=1001+i) for i, r in enumerate(rows)]


def _empty_company(cid: str, name: str) -> dict:
    return {"id": cid, "name": name, "currentPeriodId": None, "periods": {}}


def _default_data() -> dict:
    companies = {}
    for c in COMPANIES:
        companies[c["id"]] = _empty_company(c["id"], c["name"])

    # Mercury LTDA: Marzo 2026
    companies["mercury-ltda"]["currentPeriodId"] = "2026-03"
    companies["mercury-ltda"]["periods"]["2026-03"] = {
        "id": "2026-03", "nombre": "Marzo 2026",
        "banco": "Global66 COP", "cuenta": "11200502",
        "saldoInicial": 11351966.78,
        "transactions": _march_2026_txs(),
    }

    # TEST: varios períodos 2026
    companies["test"]["currentPeriodId"] = "2026-06"
    for pid, pnom in [
        ("2026-01","Enero 2026"),("2026-02","Febrero 2026"),
        ("2026-03","Marzo 2026"),("2026-04","Abril 2026"),
        ("2026-05","Mayo 2026"),("2026-06","Junio 2026"),
    ]:
        companies["test"]["periods"][pid] = {
            "id": pid, "nombre": pnom,
            "banco": "Bancolombia", "cuenta": "12345678",
            "saldoInicial": 5000000.0, "transactions": [],
        }
    # Distribuir transacciones TEST
    all_test = _test_txs()
    for t in all_test:
        pid = t["fecha"][:7]
        if pid in companies["test"]["periods"]:
            companies["test"]["periods"][pid]["transactions"].append(t)

    return {
        "version": "2.0",
        "currentCompanyId": "mercury-ltda",
        "alegra": {"email": "", "token": ""},
        "users": {},
        "companies": companies,
    }


# ── MIGRATE V1 → V2 ───────────────────────────────────────────────────────────
def _migrate(data: dict) -> dict:
    if data.get("version") == "2.0":
        return data
    # v1 had periods at top level
    old_periods = data.get("periods", {})
    old_pid     = data.get("currentPeriodId")
    new = _default_data()
    if old_periods:
        new["companies"]["mercury-ltda"]["periods"] = old_periods
        new["companies"]["mercury-ltda"]["currentPeriodId"] = old_pid
    new["alegra"] = data.get("alegra", {"email":"","token":""})
    new["users"]  = data.get("users", {})
    return new


# ── PERSISTENCE ───────────────────────────────────────────────────────────────
def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, encoding="utf-8") as f:
                raw = json.load(f)
            data = _migrate(raw)
            mx = max(
                (t.get("id",0) for co in data["companies"].values()
                 for p in co["periods"].values() for t in p["transactions"]),
                default=1000,
            )
            st.session_state["_id"] = mx
            return data
        except Exception:
            pass
    return _default_data()


def save_data(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── HELPERS ───────────────────────────────────────────────────────────────────
def fmt(n) -> str:
    try: return f"${float(n):,.2f}"
    except: return "–"


def cur_co(data: dict) -> dict | None:
    return data["companies"].get(data.get("currentCompanyId",""))


def cur_per(data: dict) -> dict | None:
    co = cur_co(data)
    if not co: return None
    return co["periods"].get(co.get("currentPeriodId",""))


def totals(txs: list) -> tuple:
    c = sum(t["monto"] for t in txs if t["tipo"]=="cargo")
    a = sum(t["monto"] for t in txs if t["tipo"]=="abono")
    return c, a


def period_months(per: dict) -> list:
    return sorted({t["fecha"][:7] for t in per["transactions"]})


def filtered_txs(per: dict) -> list:
    txs   = per["transactions"]
    mode  = st.session_state.get("filter_mode","month")
    fdate = st.session_state.get("filter_date","")
    bwm   = st.session_state.get("bw_month","")
    bwh   = st.session_state.get("bw_half",1)
    if mode=="day"  and fdate: return [t for t in txs if t["fecha"]==fdate]
    if mode=="week" and fdate:
        d   = datetime.strptime(fdate,"%Y-%m-%d")
        mon = d - timedelta(days=d.weekday())
        sun = mon + timedelta(days=6)
        return [t for t in txs if mon.date()<=datetime.strptime(t["fecha"],"%Y-%m-%d").date()<=sun.date()]
    if mode=="biweek" and bwm:
        return [t for t in txs if t["fecha"].startswith(bwm) and
                (int(t["fecha"][8:10])<=15 if bwh==1 else int(t["fecha"][8:10])>15)]
    return txs


# ── SESSION STATE ─────────────────────────────────────────────────────────────
def _init():
    ss = st.session_state
    if "data"             not in ss: ss.data             = load_data()
    if "filter_mode"      not in ss: ss.filter_mode      = "month"
    if "filter_date"      not in ss: ss.filter_date      = date.today().isoformat()
    if "bw_month"         not in ss: ss.bw_month         = ""
    if "bw_half"          not in ss: ss.bw_half          = 1
    if "dialog"           not in ss: ss.dialog           = None
    if "edit_tx_id"       not in ss: ss.edit_tx_id       = None
    if "logged_in"        not in ss: ss.logged_in        = False
    if "current_user"     not in ss: ss.current_user     = None
    if "auth_step"        not in ss: ss.auth_step        = "login"
    if "pending_email"    not in ss: ss.pending_email    = ""
    if "pending_code"     not in ss: ss.pending_code     = ""
    if "code_expiry"      not in ss: ss.code_expiry      = None
    if "email_sent"       not in ss: ss.email_sent       = False
    if "unverified_email" not in ss: ss.unverified_email = ""
    if "confirm_del_id"   not in ss: ss.confirm_del_id   = None
    if "company_selected" not in ss: ss.company_selected = False


# ── IMPORT ────────────────────────────────────────────────────────────────────
def _parse_csv(raw: str, sep: str) -> list:
    txs, bad = [], 0
    for line in raw.strip().splitlines():
        r = [c.strip().strip('"') for c in line.split(sep)]
        try:
            fecha=r[0]; desc=r[1] if len(r)>1 else ""
            if not fecha or not desc: bad+=1; continue
            monto=float(r[4].replace(",",".")) if len(r)>4 else 0
            if monto<=0: bad+=1; continue
            tipo_r = r[3].lower() if len(r)>3 else "cargo"
            tipo   = "cargo" if any(x in tipo_r for x in ["cargo","retiro","deb"]) else "abono"
            txs.append(make_tx(fecha,desc,r[2] if len(r)>2 else "",tipo,monto,
                               r[5] if len(r)>5 else "",r[6] if len(r)>6 else "",
                               r[7] if len(r)>7 else "",r[8] if len(r)>8 else "",
                               r[9] if len(r)>9 else "",r[10] if len(r)>10 else "Pendiente"))
        except: bad+=1
    return txs, bad


def _parse_excel(file_bytes: bytes) -> tuple:
    try:
        df = pd.read_excel(io.BytesIO(file_bytes))
        raw = "\t".join(df.columns)+"\n"
        for _, row in df.iterrows():
            raw += "\t".join(str(v) for v in row.values)+"\n"
        return _parse_csv(raw, "\t")
    except Exception as e:
        return [], str(e)


def _parse_pdf(file_bytes: bytes) -> tuple:
    try:
        import pdfplumber
        txs, bad = [], 0
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if not row or len(row) < 3: continue
                        r = [str(c).strip() if c else "" for c in row]
                        try:
                            fecha = r[0]; desc = r[1]
                            monto_str = next((x for x in r[2:] if x.replace(".","").replace(",","").replace("-","").strip().isdigit()), "0")
                            monto = abs(float(monto_str.replace(",","").replace(".",""))) / 100
                            if not fecha or len(fecha)<8 or monto<=0: bad+=1; continue
                            txs.append(make_tx(fecha,desc,"","cargo",monto))
                        except: bad+=1
        return txs, bad
    except Exception as e:
        return [], str(e)


# ── EXPORT ────────────────────────────────────────────────────────────────────
def _export_csv(txs: list) -> bytes:
    df = _txs_to_df(txs)
    return df.to_csv(index=False).encode("utf-8-sig")


def _export_excel(txs: list) -> bytes:
    df = _txs_to_df(txs)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Conciliacion")
    return buf.getvalue()


def _export_pdf(txs: list, per: dict) -> bytes:
    import contextlib, io as _sio
    buf = _sio.StringIO()
    try:
        from fpdf import FPDF
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            pdf = FPDF(orientation="L", unit="mm", format="A4")
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, f"Conciliacion Bancaria - {per.get('nombre','')}", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 7)
            headers = ["Fecha", "Descripcion", "Ref", "Cargo ($)", "Abono ($)", "Concepto", "Cuenta", "Origen/Destino", "Estado"]
            widths  = [22, 60, 26, 24, 24, 32, 22, 34, 22]
            pdf.set_fill_color(44, 62, 80); pdf.set_text_color(255, 255, 255)
            for h, w in zip(headers, widths):
                pdf.cell(w, 7, h, border=1, fill=True)
            pdf.ln()
            pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", "", 6)
            for i, t in enumerate(txs):
                cargo = fmt(t["monto"]) if t["tipo"] == "cargo" else "$0.00"
                abono = fmt(t["monto"]) if t["tipo"] == "abono" else "$0.00"
                vals  = [
                    t["fecha"], t["descripcion"][:40], t["movimiento"][:14],
                    cargo, abono, t.get("concepto","")[:22], t.get("cuenta","")[:12],
                    t.get("origen", t.get("contacto",""))[:20], t["estado"],
                ]
                r, g, b = (245, 245, 245) if i % 2 == 0 else (255, 255, 255)
                pdf.set_fill_color(r, g, b)
                for v, w in zip(vals, widths):
                    pdf.cell(w, 6, str(v), border=1, fill=True)
                pdf.ln()
            raw = pdf.output()
        return bytes(raw) if raw is not None else b""
    except Exception as e:
        return f"Error generando PDF: {e}".encode("utf-8")


def _txs_to_df(txs: list) -> pd.DataFrame:
    rows = []
    for t in txs:
        rows.append({
            "Fecha":       t["fecha"],
            "Descripcion": t["descripcion"],
            "N Movimiento":t["movimiento"],
            "Cargo":       t["monto"] if t["tipo"]=="cargo" else 0,
            "Abono":       t["monto"] if t["tipo"]=="abono" else 0,
            "Concepto Alegra": t["concepto"],
            "Cuenta Contable": t["cuenta"],
            "Ref Cuenta":  t["cuentaRef"],
            "Origen/Destino": t.get("origen",t.get("contacto","")),
            "Notas":       t["nota"],
            "Estado":      t["estado"],
        })
    return pd.DataFrame(rows)


# ── AUTH PAGE ─────────────────────────────────────────────────────────────────
def _auth_page():
    data = st.session_state.data
    st.markdown('<div class="auth-header"><div style="font-size:2rem">🏦</div>'
                '<h2 style="margin:8px 0 4px;font-size:1.2rem">Conciliación Bancaria</h2>'
                '<p style="margin:0;opacity:.75;font-size:.8rem">Mercury Methods Ltda</p></div>',
                unsafe_allow_html=True)

    step = st.session_state.auth_step

    if step == "login":
        tab_in, tab_reg = st.tabs(["Iniciar sesión","Registrarse"])

        with tab_in:
            with st.form("form_login"):
                email    = st.text_input("Correo", placeholder="correo@empresa.com")
                password = st.text_input("Contraseña", type="password")
                sub = st.form_submit_button("Ingresar", use_container_width=True, type="primary")
            if sub:
                ok, err = _auth.authenticate(data, email, password)
                if ok:
                    st.session_state.logged_in       = True
                    st.session_state.current_user    = email.strip().lower()
                    st.session_state.unverified_email = ""
                    st.session_state.company_selected = False
                    save_data(data); st.rerun()
                elif "pendiente" in err:
                    st.session_state.unverified_email = email.strip().lower()
                else:
                    st.error(err); st.session_state.unverified_email = ""

            if st.session_state.get("unverified_email"):
                st.warning("Cuenta pendiente de verificación.")
                if st.button("📧 Reenviar código", use_container_width=True):
                    em   = st.session_state.unverified_email
                    code = _auth.generate_code()
                    sent,_ = _auth.send_code_email(em,code)
                    st.session_state.update(pending_email=em,pending_code=code,
                        code_expiry=datetime.now()+timedelta(minutes=10),
                        email_sent=sent, auth_step="verify", unverified_email="")
                    st.rerun()

        with tab_reg:
            with st.form("form_reg"):
                name  = st.text_input("Nombre completo")
                email = st.text_input("Correo", placeholder="correo@empresa.com")
                pw    = st.text_input("Contraseña (mín. 6 caracteres)", type="password")
                pw2   = st.text_input("Confirmar contraseña", type="password")
                sub   = st.form_submit_button("Registrarse", use_container_width=True, type="primary")
            if sub:
                if pw != pw2: st.error("Las contraseñas no coinciden.")
                else:
                    ok, err = _auth.register_user(data, email, pw, name)
                    if not ok: st.error(err)
                    else:
                        code = _auth.generate_code()
                        sent,_ = _auth.send_code_email(email.strip().lower(),code)
                        st.session_state.update(pending_email=email.strip().lower(),
                            pending_code=code, code_expiry=datetime.now()+timedelta(minutes=10),
                            email_sent=sent, auth_step="verify")
                        save_data(data); st.rerun()

    elif step == "verify":
        em   = st.session_state.pending_email
        sent = st.session_state.email_sent
        if sent:
            st.success(f"📧 Código enviado a **{em}**")
        else:
            st.warning("SMTP no configurado — use el código de abajo")
            st.markdown(
                f'<div style="text-align:center;background:#f5f5f5;border-radius:8px;padding:20px;margin:10px 0;">'
                f'<p style="color:#757575;margin:0 0 6px;font-size:.8rem">Código de verificación:</p>'
                f'<span style="font-size:2.8rem;font-weight:700;letter-spacing:12px;color:#2c3e50">'
                f'{st.session_state.pending_code}</span>'
                f'<p style="color:#757575;margin:6px 0 0;font-size:.75rem">Válido 10 min</p></div>',
                unsafe_allow_html=True)

        with st.form("form_verify"):
            code_in = st.text_input("Código de 6 dígitos", max_chars=6, placeholder="123456")
            sub = st.form_submit_button("Verificar cuenta", use_container_width=True, type="primary")
        if sub:
            if _auth.code_expired():
                st.error("Código expirado. Vuelva al inicio.")
                st.session_state.auth_step = "login"; st.rerun()
            elif code_in.strip() != st.session_state.pending_code:
                st.error("Código incorrecto.")
            else:
                _auth.mark_verified(data, em)
                st.session_state.update(logged_in=True, current_user=em,
                    auth_step="login", pending_code="")
                save_data(data); st.rerun()

        c1,c2 = st.columns(2)
        if c1.button("🔄 Reenviar", use_container_width=True):
            code=_auth.generate_code(); sent,_=_auth.send_code_email(em,code)
            st.session_state.update(pending_code=code, email_sent=sent,
                code_expiry=datetime.now()+timedelta(minutes=10)); st.rerun()
        if c2.button("← Login", use_container_width=True):
            st.session_state.auth_step="login"; st.rerun()


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
def _sidebar():
    data = st.session_state.data
    ss   = st.session_state
    co   = cur_co(data) if ss.company_selected else None

    # ── Encabezado: nombre empresa seleccionada o genérico ───────────────
    users = _auth.get_users(data)
    uname = users.get(ss.current_user,{}).get("name","") or ss.current_user
    title = co.get("name","") if co else "Portal de Conciliaciones"
    st.sidebar.markdown(f"**{title}**\n\n👤 {uname}")
    if st.sidebar.button("Cerrar sesión", use_container_width=True):
        ss.logged_in=False; ss.current_user=None; ss.company_selected=False; st.rerun()
    st.sidebar.divider()

    # ── Empresas (siempre visible) ────────────────────────────────────────
    st.sidebar.markdown("### 🏢 Empresas")
    cur_co_id = data.get("currentCompanyId","")
    for c in COMPANIES:
        is_active = c["id"] == cur_co_id and ss.company_selected
        label = f"{'▶  ' if is_active else ''}{c['name']}"
        if st.sidebar.button(label, use_container_width=True,
                              type="primary" if is_active else "secondary",
                              key=f"co_{c['id']}"):
            data["currentCompanyId"] = c["id"]
            ss.company_selected = True
            save_data(data); st.rerun()

    # ── Resto solo aparece si hay empresa seleccionada ────────────────────
    if not ss.company_selected or not co:
        return

    st.sidebar.divider()

    # ── Período ─────────────────────────────────────────────────────────
    st.sidebar.markdown("### 📅 Período")
    periods  = sorted(co["periods"].values(), key=lambda p: p["id"], reverse=True)
    per_ids  = [p["id"] for p in periods]
    per_lbls = [p["nombre"] for p in periods]
    cur_pid  = co.get("currentPeriodId","")
    per      = None

    if per_ids:
        cur_i = per_ids.index(cur_pid) if cur_pid in per_ids else 0
        sel_i = st.sidebar.selectbox("Período activo", range(len(per_lbls)),
                                      format_func=lambda i: per_lbls[i], index=cur_i)
        if per_ids[sel_i] != cur_pid:
            co["currentPeriodId"] = per_ids[sel_i]
            save_data(data); st.rerun()
        per = cur_per(data)
    else:
        st.sidebar.info("Sin períodos. Use ➕ Nuevo.")

    pc1, pc2 = st.sidebar.columns(2)
    if pc1.button("➕ Nuevo",  use_container_width=True): ss.dialog="new_period"; st.rerun()
    if pc2.button("✏️ Editar", use_container_width=True):
        if per: ss.dialog="edit_period"; st.rerun()

    st.sidebar.divider()

    # ── Banco ────────────────────────────────────────────────────────────
    if per:
        st.sidebar.markdown("### 🏦 Banco")
        bi = BANCOS.index(per["banco"]) if per.get("banco") in BANCOS else 0
        nb = st.sidebar.selectbox("Banco", BANCOS, index=bi, label_visibility="collapsed")
        if nb != per.get("banco"):
            per["banco"] = nb; save_data(data); st.rerun()
        st.sidebar.divider()

    # ── Alegra ──────────────────────────────────────────────────────────
    st.sidebar.markdown("### 🔗 Alegra")
    cfg   = data.setdefault("alegra",{"email":"","token":""})
    ok_al = bool(cfg.get("email") and cfg.get("token"))
    st.sidebar.caption("✅ Credenciales OK" if ok_al else "⚙️ Sin configurar")
    with st.sidebar.expander("Configurar"):
        em2 = st.text_input("Email Alegra", value=cfg.get("email",""), key="al_em")
        tk2 = st.text_input("Token API", value=cfg.get("token",""), type="password", key="al_tk")
        if st.button("💾 Guardar", use_container_width=True, key="al_save"):
            cfg["email"]=em2.strip(); cfg["token"]=tk2.strip()
            save_data(data); st.success("Guardado")

    # (sección Datos eliminada)


# ── MÉTRICAS ──────────────────────────────────────────────────────────────────
def _metrics(per: dict):
    txs   = per["transactions"]
    c,a   = totals(txs)
    sf    = per["saldoInicial"] - c + a
    conc  = [t for t in txs if t["estado"]=="Conciliado"]
    pend  = [t for t in txs if t["estado"]=="Pendiente"]
    mc,ma = totals(conc)
    monto_conc = mc + ma

    cols = st.columns(7)
    data_metrics = [
        ("Saldo Inicial",      fmt(per["saldoInicial"]), None,          "normal"),
        ("Total Cargos",       fmt(c),                   f"-{fmt(c)}",  "inverse"),
        ("Total Abonos",       fmt(a),                   fmt(a),        "normal"),
        ("Saldo Final",        fmt(sf),                  None,          "normal"),
        ("Conciliados Alegra", len(conc),                None,          "normal"),
        ("Monto Conciliado",   fmt(monto_conc),          None,          "normal"),
        ("Pendientes",         len(pend),                None,          "inverse"),
    ]
    for col,(lbl,val,dlt,dc) in zip(cols,data_metrics):
        with col: st.metric(lbl,val,delta=dlt,delta_color=dc)


# ── PERÍODO + FILTROS (combinados) ────────────────────────────────────────────
def _period_filters(per: dict):
    c1,c2,c3 = st.columns([4,4,3])
    with c1:
        mode = st.radio("Vista",["Mes completo","Día","Semana","Quincena"],horizontal=True)
        st.session_state.filter_mode = {"Mes completo":"month","Día":"day",
                                         "Semana":"week","Quincena":"biweek"}[mode]
    with c2:
        m = st.session_state.filter_mode
        if m=="day":
            d = st.date_input("Fecha", key="fd_d")
            st.session_state.filter_date = d.isoformat()
        elif m=="week":
            d = st.date_input("Fecha en semana", key="fd_w")
            st.session_state.filter_date = d.isoformat()
            mon = d-timedelta(days=d.weekday()); sun=mon+timedelta(days=6)
            st.caption(f"{mon:%d/%m} – {sun:%d/%m/%Y}")
        elif m=="biweek":
            months = sorted({t["fecha"][:7] for t in per["transactions"]})
            if months:
                ms = st.selectbox("Mes",months,
                    format_func=lambda m: datetime(int(m[:4]),int(m[5:]),1).strftime("%B %Y").capitalize(),
                    key="bw_ms")
                st.session_state.bw_month = ms
            st.session_state.bw_half = st.radio("Q",[1,2],horizontal=True,
                format_func=lambda h:"1ª (1–15)" if h==1 else "2ª (16–fin)",key="bw_h")
    with c3:
        filt  = filtered_txs(per)
        fc,fa = totals(filt)
        st.caption(f"**{len(filt)}** mov.  |  Cargos **{fmt(fc)}**  |  Abonos **{fmt(fa)}**")


# ── TABLA PRINCIPAL ───────────────────────────────────────────────────────────
def _table(per: dict):
    data = st.session_state.data
    txs  = sorted(filtered_txs(per), key=lambda t:(t["fecha"],t["id"]))
    if not txs:
        st.info("Sin movimientos en este filtro.")
        return

    df = pd.DataFrame(txs)
    df["Cargo ($)"] = df.apply(lambda r: r["monto"] if r["tipo"]=="cargo" else 0.0, axis=1)
    df["Abono ($)"] = df.apply(lambda r: r["monto"] if r["tipo"]=="abono" else 0.0, axis=1)
    df["Origen/Destino"] = df.apply(lambda r: r.get("origen") or r.get("contacto",""), axis=1)

    show_cols = ["id","fecha","descripcion","movimiento",
                 "Cargo ($)","Abono ($)","concepto","cuenta","cuentaRef",
                 "Origen/Destino","nota","estado"]
    df_v = df[show_cols].copy()

    edited = st.data_editor(
        df_v,
        column_config={
            "id":             None,
            "fecha":          st.column_config.TextColumn("Fecha",           disabled=True, width=88),
            "descripcion":    st.column_config.TextColumn("Descripción",     disabled=True, width=200),
            "movimiento":     st.column_config.TextColumn("N° Mov.",         disabled=True, width=110),
            "Cargo ($)":      st.column_config.NumberColumn("Cargo ($)",     disabled=True, format="$%,.2f", width=110),
            "Abono ($)":      st.column_config.NumberColumn("Abono ($)",     disabled=True, format="$%,.2f", width=110),
            "concepto":       st.column_config.TextColumn("Concepto Alegra", width=130),
            "cuenta":         st.column_config.TextColumn("Cta. Contable",   width=100),
            "cuentaRef":      st.column_config.TextColumn("Ref. Cuenta",     width=120),
            "Origen/Destino": st.column_config.TextColumn("Origen/Destino",  width=120),
            "nota":           st.column_config.TextColumn("Notas",           width=120),
            "estado":         st.column_config.SelectboxColumn("Estado",     options=ESTADOS, disabled=True, width=110),
        },
        disabled=["fecha","descripcion","movimiento","Cargo ($)","Abono ($)","estado"],
        hide_index=True, use_container_width=True, num_rows="fixed", key="tx_tbl",
    )

    # Guardar edits inline
    editable = ["concepto","cuenta","cuentaRef","nota"]
    id_map   = {t["id"]:t for t in per["transactions"]}
    changed  = False
    for i,row in edited.iterrows():
        tid = df_v.iloc[i]["id"]; t = id_map.get(tid)
        if not t: continue
        # Origen/Destino
        nv = row["Origen/Destino"] or ""
        if t.get("origen",t.get("contacto","")) != nv:
            t["origen"] = nv; changed=True
        for f in editable:
            nv = row[f] or ""
            if str(t.get(f,"")) != str(nv):
                t[f]=nv; changed=True
    if changed: save_data(data)

    # ── Controles de fila ────────────────────────────────────────────────
    st.markdown("---")
    lbl = {t["id"]: f"{t['fecha']}  |  {t['descripcion'][:45]}  |  {fmt(t['monto'])} ({'↑' if t['tipo']=='abono' else '↓'})"
           for t in txs}
    ra1,ra2,ra3,_ = st.columns([5,1,1,2])
    with ra1:
        sel = st.selectbox("Seleccione fila para acción", list(lbl.keys()),
                            format_func=lambda i:lbl[i], label_visibility="collapsed")
    with ra2:
        if st.button("＋ Agregar debajo", use_container_width=True, help="Insertar fila en blanco debajo"):
            st.session_state.dialog    = "tx"
            st.session_state.edit_tx_id = None
            st.session_state.insert_after = sel
            st.rerun()
    with ra3:
        if st.button("🗑 Eliminar", use_container_width=True, help="Eliminar esta fila"):
            st.session_state.confirm_del_id = sel
            st.rerun()

    # Confirmar eliminación
    if st.session_state.confirm_del_id:
        did  = st.session_state.confirm_del_id
        desc = lbl.get(did,"este movimiento")
        st.warning(f"¿Eliminar **{desc}**?")
        c1,c2,_ = st.columns([1,1,5])
        if c1.button("Sí, eliminar", type="primary"):
            per["transactions"] = [t for t in per["transactions"] if t["id"]!=did]
            st.session_state.confirm_del_id = None
            save_data(data); st.rerun()
        if c2.button("Cancelar"):
            st.session_state.confirm_del_id = None; st.rerun()

    # ── Importar / Exportar (pie de tabla) ──────────────────────────────
    st.markdown("---")
    today = date.today().isoformat()

    imp_col, exp_col = st.columns([1, 1])

    with imp_col:
        st.markdown("**⬆️ Importar extracto**")
        i1, i2, i3 = st.columns(3)
        with i1:
            csv_f = st.file_uploader("CSV", type=["csv","txt"], key="up_csv_tbl")
            if csv_f:
                raw = csv_f.read().decode("utf-8", errors="replace")
                new_txs, bad = _parse_csv(raw, ",")
                if st.button(f"Confirmar {len(new_txs)} filas", key="ok_csv"):
                    per["transactions"].extend(new_txs); save_data(data); st.rerun()
        with i2:
            xls_f = st.file_uploader("Excel", type=["xlsx","xls"], key="up_xls_tbl")
            if xls_f:
                new_txs, bad = _parse_excel(xls_f.read())
                if st.button(f"Confirmar {len(new_txs)} filas", key="ok_xls"):
                    per["transactions"].extend(new_txs); save_data(data); st.rerun()
        with i3:
            pdf_f = st.file_uploader("PDF", type=["pdf"], key="up_pdf_tbl")
            if pdf_f:
                new_txs, bad = _parse_pdf(pdf_f.read())
                st.caption(f"{len(new_txs)} detectadas, {bad} errores")
                if new_txs and st.button(f"Confirmar {len(new_txs)} filas", key="ok_pdf"):
                    per["transactions"].extend(new_txs); save_data(data); st.rerun()

    with exp_col:
        st.markdown("**⬇️ Exportar**")
        # Pre-calcular los bytes antes de crear columnas para evitar output a stdout
        csv_bytes   = _export_csv(txs)
        excel_bytes = _export_excel(txs)
        pdf_bytes   = _export_pdf(txs, per)
        e1, e2, e3  = st.columns(3)
        e1.download_button("⬇️ CSV",   csv_bytes,   f"conciliacion_{today}.csv",  "text/csv", use_container_width=True)
        e2.download_button("⬇️ Excel", excel_bytes, f"conciliacion_{today}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        e3.download_button("⬇️ PDF",   pdf_bytes,   f"conciliacion_{today}.pdf",  "application/pdf", use_container_width=True)


# _import_section eliminada — import integrado en pie de _table()


# ── DIÁLOGOS ─────────────────────────────────────────────────────────────────
@st.dialog("Período de conciliación")
def _dlg_period():
    data = st.session_state.data
    co   = cur_co(data)
    edit = st.session_state.dialog=="edit_period"
    per  = cur_per(data) if edit else None
    st.subheader("Editar período" if edit else "Nuevo período")

    nombre = st.text_input("Nombre *", value=per["nombre"] if per else "")
    if edit:
        st.text_input("ID", value=per["id"], disabled=True); pid=per["id"]
    else:
        pid = st.text_input("ID período (YYYY-MM)", placeholder="2026-07", max_chars=7)

    c1,c2 = st.columns(2)
    with c1:
        si    = st.number_input("Saldo inicial ($)", value=float(per["saldoInicial"]) if per else 0.0, step=0.01)
        banco = st.selectbox("Banco",BANCOS,index=BANCOS.index(per["banco"]) if per and per.get("banco") in BANCOS else 0)
    with c2:
        cuenta = st.text_input("N° Cuenta", value=per.get("cuenta","") if per else "")

    oc,cc = st.columns(2)
    if cc.button("Cancelar", use_container_width=True):
        st.session_state.dialog=None; st.rerun()
    if oc.button("Guardar", type="primary", use_container_width=True):
        if not nombre.strip(): st.error("Nombre requerido."); return
        if not edit:
            if not pid or len(pid)!=7 or pid[4]!="-": st.error("ID inválido."); return
            if pid in co["periods"]: st.error("Ya existe."); return
            co["periods"][pid]={"id":pid,"nombre":nombre,"banco":banco,
                                "cuenta":cuenta,"saldoInicial":si,"transactions":[]}
            co["currentPeriodId"]=pid
        else:
            per.update({"nombre":nombre,"banco":banco,"cuenta":cuenta,"saldoInicial":si})
        save_data(data); st.session_state.dialog=None; st.rerun()


@st.dialog("Movimiento bancario", width="large")
def _dlg_tx():
    data    = st.session_state.data
    per     = cur_per(data)
    eid     = st.session_state.edit_tx_id
    ex      = next((t for t in per["transactions"] if t["id"]==eid),None) if eid else None
    st.subheader("Editar movimiento" if ex else "Agregar movimiento")

    c1,c2 = st.columns(2)
    with c1:
        fecha = st.date_input("Fecha *", value=datetime.strptime(ex["fecha"],"%Y-%m-%d").date() if ex else date.today())
        tipo  = st.selectbox("Tipo *",["cargo","abono"], index=0 if not ex or ex["tipo"]=="cargo" else 1)
    with c2:
        monto = st.number_input("Monto * ($)", min_value=0.01, step=0.01, value=float(ex["monto"]) if ex else 0.01)
        mov   = st.text_input("N° Movimiento", value=ex.get("movimiento","") if ex else "")

    desc = st.text_input("Descripción *", value=ex.get("descripcion","") if ex else "")
    c3,c4 = st.columns(2)
    with c3:
        concepto   = st.text_input("Concepto Alegra",  value=ex.get("concepto","") if ex else "")
        cuenta     = st.text_input("Cuenta Contable",  value=ex.get("cuenta","") if ex else "")
        cuenta_ref = st.text_input("Ref. Cuenta",      value=ex.get("cuentaRef","") if ex else "")
    with c4:
        origen = st.text_input("Origen/Destino", value=ex.get("origen",ex.get("contacto","")) if ex else "")
        estado = st.selectbox("Estado",ESTADOS, index=ESTADOS.index(ex["estado"]) if ex and ex["estado"] in ESTADOS else 0)
        nota   = st.text_input("Notas", value=ex.get("nota","") if ex else "")

    oc,cc = st.columns(2)
    if cc.button("Cancelar", use_container_width=True):
        st.session_state.dialog=None; st.session_state.edit_tx_id=None; st.rerun()
    if oc.button("Guardar", type="primary", use_container_width=True):
        if not desc.strip(): st.error("Descripción requerida."); return
        t = make_tx(fecha.isoformat(),desc,mov,tipo,monto,concepto,cuenta,cuenta_ref,origen,nota,estado,tx_id=eid)
        if ex:
            idx = next(i for i,x in enumerate(per["transactions"]) if x["id"]==eid)
            per["transactions"][idx]=t
        else:
            after = st.session_state.get("insert_after")
            if after:
                idx = next((i for i,x in enumerate(per["transactions"]) if x["id"]==after), len(per["transactions"])-1)
                per["transactions"].insert(idx+1,t)
                st.session_state.insert_after=None
            else:
                per["transactions"].append(t)
        save_data(data); st.session_state.dialog=None; st.session_state.edit_tx_id=None; st.rerun()


# ── ALEGRA PANEL ──────────────────────────────────────────────────────────────
def _alegra_panel():
    data = st.session_state.data
    cfg  = data.get("alegra",{})
    ok   = bool(cfg.get("email") and cfg.get("token"))
    st.markdown("### 🔗 Integración con Alegra")
    if ok: st.success(f"✅ Credenciales configuradas — **{cfg.get('email','')}**")
    else:  st.warning("⚙️ Credenciales no configuradas. Configure en el panel lateral.")
    st.markdown("""
**Para conectar:**
1. Alegra → Configuración → Mi perfil → **Token de API**
2. Copie el token y péguelo en **Panel lateral → Alegra → Configurar**

> Importación automática de movimientos disponible próximamente.
""")


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    _init()

    if not st.session_state.logged_in:
        _auth_page(); return

    _sidebar()

    data = st.session_state.data

    # ── Pantalla de bienvenida (ninguna empresa seleccionada) ─────────────
    if not st.session_state.company_selected:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;
                    justify-content:center;height:65vh;text-align:center;">
            <div style="font-size:3.5rem;margin-bottom:16px;">🏦</div>
            <h1 style="font-size:2.4rem;font-weight:800;color:#2c3e50;
                       letter-spacing:2px;margin-bottom:12px;">
                PORTAL DE CONCILIACIONES
            </h1>
            <p style="font-size:1rem;color:#757575;max-width:360px;line-height:1.6;">
                Seleccione una empresa en el panel izquierdo para comenzar
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    co  = cur_co(data)
    per = cur_per(data)

    # Diálogos
    dlg = st.session_state.dialog
    if dlg in ("new_period","edit_period"):  _dlg_period()
    elif dlg == "tx":                        _dlg_tx()
    elif dlg == "delete_period":
        if per:
            st.warning(f"¿Eliminar **{per['nombre']}**? No se puede deshacer.", icon="⚠️")
            c1,c2,_ = st.columns([1,1,5])
            if c1.button("Sí, eliminar", type="primary"):
                del co["periods"][co["currentPeriodId"]]
                co["currentPeriodId"] = list(co["periods"].keys())[0] if co["periods"] else None
                st.session_state.dialog=None; save_data(data); st.rerun()
            if c2.button("Cancelar"):
                st.session_state.dialog=None; st.rerun()
            return

    if not co:
        st.info("Seleccione una empresa en el panel lateral."); return

    # Header
    co_name  = co.get("name","")
    per_info = f"{per.get('nombre','')} | Cta: {per.get('cuenta','–')} | {per.get('banco','')}" if per else "Sin período"
    st.markdown(
        f'<div style="background:#2c3e50;color:#fff;padding:12px 20px;border-radius:8px;'
        f'margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;">'
        f'<strong style="font-size:1.05rem">🏦 Conciliación Bancaria — {co_name}</strong>'
        f'<span style="font-size:.78rem;opacity:.75">{per_info}</span></div>',
        unsafe_allow_html=True)

    if not per:
        st.info("Sin períodos. Use ➕ Nuevo en el panel lateral para crear el primero.")
        return

    # Métricas
    _metrics(per)
    st.markdown("")

    # Tabs
    tab_mov, tab_per, tab_alegra = st.tabs(["📊 Movimientos", "📅 Período y Filtros", "🔗 Alegra"])

    with tab_mov:
        _table(per)

    with tab_per:
        _period_filters(per)

    with tab_alegra:
        _alegra_panel()


if __name__ == "__main__":
    main()
