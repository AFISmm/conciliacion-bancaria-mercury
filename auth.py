"""Módulo de autenticación – Conciliación Bancaria Mercury Methods."""

import hashlib
import os
import secrets
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import streamlit as st


# ── CONTRASEÑAS ──────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    salt = os.urandom(16)
    key  = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return salt.hex() + ":" + key.hex()


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, key_hex = stored.split(":")
        salt = bytes.fromhex(salt_hex)
        key  = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
        return key.hex() == key_hex
    except Exception:
        return False


# ── CÓDIGO DE VERIFICACIÓN ───────────────────────────────────────────────────
def generate_code() -> str:
    return str(secrets.randbelow(900_000) + 100_000)   # 6 dígitos


def code_expired() -> bool:
    expiry = st.session_state.get("code_expiry")
    if expiry is None:
        return True
    return datetime.now() > expiry


# ── EMAIL ─────────────────────────────────────────────────────────────────────
def send_code_email(to_email: str, code: str) -> tuple:
    """Devuelve (enviado: bool, mensaje: str)."""
    try:
        cfg      = st.secrets.get("smtp", {})
        host     = cfg.get("host", "smtp.gmail.com")
        port     = int(cfg.get("port", 465))
        user     = cfg.get("user", "")
        password = cfg.get("password", "")
        nombre   = cfg.get("from_name", "Conciliación Bancaria Mercury")
    except Exception:
        return False, "SMTP_NOT_CONFIGURED"

    if not (user and password):
        return False, "SMTP_NOT_CONFIGURED"

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;">
      <div style="background:#2c3e50;color:#fff;padding:22px 28px;border-radius:8px 8px 0 0;">
        <h2 style="margin:0;font-size:1.2rem;">🏦 Conciliación Bancaria</h2>
        <p  style="margin:4px 0 0;opacity:.75;font-size:.8rem;">Mercury Methods Ltda</p>
      </div>
      <div style="padding:32px 28px;border:1px solid #e0e0e0;border-top:none;border-radius:0 0 8px 8px;">
        <p style="color:#424242;margin-top:0;">Su código de verificación es:</p>
        <div style="text-align:center;margin:28px 0;">
          <span style="font-size:42px;font-weight:700;letter-spacing:14px;
                       color:#2c3e50;background:#f5f5f5;padding:14px 28px;border-radius:8px;">
            {code}
          </span>
        </div>
        <p style="color:#757575;font-size:.78rem;">
          Este código expira en <strong>10 minutos</strong>.<br>
          Si no solicitó este código, ignore este mensaje.
        </p>
      </div>
    </div>
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["From"]    = f"{nombre} <{user}>"
        msg["To"]      = to_email
        msg["Subject"] = "Código de verificación – Conciliación Bancaria Mercury"
        msg.attach(MIMEText(html, "html", "utf-8"))

        if port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=10) as srv:
                srv.login(user, password)
                srv.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=10) as srv:
                srv.ehlo()
                srv.starttls()
                srv.login(user, password)
                srv.send_message(msg)
        return True, ""
    except Exception as e:
        return False, str(e)


# ── USUARIOS ─────────────────────────────────────────────────────────────────
def get_users(data: dict) -> dict:
    return data.setdefault("users", {})


def register_user(data: dict, email: str, password: str, name: str = "") -> tuple:
    """Devuelve (ok: bool, error: str)."""
    email = email.strip().lower()
    if not email or "@" not in email:
        return False, "Correo electrónico inválido."
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."
    users = get_users(data)
    if email in users:
        return False, "Este correo ya está registrado."
    users[email] = {
        "name":          name.strip(),
        "password_hash": hash_password(password),
        "verified":      False,
        "created_at":    datetime.now().isoformat(),
    }
    return True, ""


def mark_verified(data: dict, email: str) -> None:
    users = get_users(data)
    if email in users:
        users[email]["verified"] = True


def authenticate(data: dict, email: str, password: str) -> tuple:
    """Devuelve (ok: bool, error: str)."""
    email = email.strip().lower()
    users = get_users(data)
    user  = users.get(email)
    if not user:
        return False, "Correo no registrado."
    if not verify_password(password, user.get("password_hash", "")):
        return False, "Contraseña incorrecta."
    if not user.get("verified"):
        return False, "Cuenta pendiente de verificación. Revise su correo."
    return True, ""
