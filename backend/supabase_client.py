# -*- coding: utf-8 -*-
"""Cliente Supabase (REST) para memoria de chat."""
import os
import json
import urllib.request
import urllib.error
import urllib.parse

URL = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
# Clave SECRETA del servidor (sb_secret_… o service_role). La tabla no admite la clave pública/anon:
# la lectura anónima exponía todas las conversaciones. Nunca pongas esta clave en el frontend ni en el repo.
KEY = (os.environ.get("SUPABASE_SECRET_KEY") or os.environ.get("SUPABASE_KEY") or "").strip()
TABLE = os.environ.get("SUPABASE_CHAT_TABLE", "chat_messages")

def is_configured():
    return bool(URL and KEY)

def _headers():
    h = {
        "apikey": KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    # Las claves legadas son JWT y van también como Bearer; las nuevas sb_secret_ solo en apikey.
    if KEY.startswith("eyJ"):
        h["Authorization"] = f"Bearer {KEY}"
    return h

def save_message(session_id, role, content):
    if not is_configured():
        return False
    data = json.dumps({"session_id": session_id, "role": role, "content": content}).encode("utf-8")
    req = urllib.request.Request(f"{URL}/rest/v1/{TABLE}", data=data, headers=_headers(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status in (200, 201, 204)
    except Exception:
        return False

def get_history(session_id, limit=20):
    if not is_configured():
        return []
    q = urllib.parse.urlencode({"session_id": f"eq.{session_id}", "order": "created_at.asc", "limit": str(limit)}, safe=".,")
    req = urllib.request.Request(f"{URL}/rest/v1/{TABLE}?{q}", headers=_headers(), method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8")
            rows = json.loads(raw)
            return [{"role": r["role"], "content": r["content"]} for r in rows]
    except Exception:
        return []
