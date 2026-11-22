# -*- coding: utf-8 -*-
import os, sys, json, sqlite3, random, string
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env = os.path.join(BASE_DIR, ".env")
if os.path.isfile(_env):
    with open(_env, encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith("#") or "=" not in line: continue
            k,v=line.split("=",1)
            k=k.strip(); v=v.strip().strip('"').strip("'")
            if k and k not in os.environ: os.environ[k]=v

sys.path.insert(0, os.path.join(BASE_DIR, "backend"))
from menu import MENU, menu_text, menu_flat

app = FastAPI(title="Puerto A&M Landing", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
DB_PATH = os.path.join(BASE_DIR, "data", "app.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def _conn():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c

with _conn() as c:
    c.execute("""CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, phone TEXT, message TEXT, source TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS reservations (id INTEGER PRIMARY KEY AUTOINCREMENT, folio TEXT, name TEXT, phone TEXT, date TEXT, time TEXT, people INTEGER, notes TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, folio TEXT, mode TEXT, items TEXT, total REAL, name TEXT, phone TEXT, address TEXT, notes TEXT, created_at TEXT)""")

# load SOULMD
SOULMD_PATH = os.path.join(BASE_DIR, "SOULMD.md")
SOULMD = ""
if os.path.isfile(SOULMD_PATH):
    with open(SOULMD_PATH, encoding="utf-8") as f:
        SOULMD = f.read()

# llm client
try:
    import llm_client
except Exception:
    llm_client = None

def _folio(prefix):
    return prefix + "-" + "".join(random.choices(string.digits, k=4))

@app.get("/api/health")
def health():
    return {"status":"ok"}

@app.get("/api/public/info")
def public_info():
    return {"name":"Puerto A&M Gourmet","tagline":"Experiencia gastronómica con sabor a puerto","location":"Paraíso, Tabasco, México","phone":"(933) 688 55 85","email":"contacto@puertoamgourmet.mx","services":["Restaurante","Catering para eventos","Comedor industrial"],"hours":"Lun-Dom 8:00-22:00"}

@app.get("/api/menu")
def get_menu():
    return {"menu": MENU, "flat": menu_flat()}

@app.post("/api/leads")
async def create_lead(request: Request):
    body=await request.json()
    name=(body.get("name") or "").strip()
    email=(body.get("email") or "").strip()
    phone=(body.get("phone") or "").strip()
    message=(body.get("message") or "").strip()
    if not name or not (email or phone):
        raise HTTPException(status_code=400, detail="Nombre y email o teléfono son obligatorios")
    with _conn() as c:
        c.execute("INSERT INTO leads (name,email,phone,message,source,created_at) VALUES (?,?,?,?,?,?)",
                  (name,email,phone,message,body.get("source","web"),datetime.utcnow().isoformat()))
    return {"ok":True}

@app.post("/api/reservations")
async def create_reservation(request: Request):
    body=await request.json()
    name=(body.get("name") or "").strip()
    phone=(body.get("phone") or "").strip()
    date=(body.get("date") or "").strip()
    time=(body.get("time") or "").strip()
    people=int(body.get("people") or 1)
    notes=(body.get("notes") or "").strip()
    if not name or not phone or not date or not time:
        raise HTTPException(status_code=400, detail="Faltan datos de la reservación")
    folio=_folio("RES")
    with _conn() as c:
        c.execute("INSERT INTO reservations (folio,name,phone,date,time,people,notes,created_at) VALUES (?,?,?,?,?,?,?,?)",
                  (folio,name,phone,date,time,people,notes,datetime.utcnow().isoformat()))
    return {"ok":True,"folio":folio,"message":f"Reservación confirmada para {name}: {date} a las {time} para {people} personas. Folio {folio}."}

@app.post("/api/orders")
async def create_order(request: Request):
    body=await request.json()
    mode=(body.get("mode") or "").strip()
    items=body.get("items") or []
    name=(body.get("name") or "").strip()
    phone=(body.get("phone") or "").strip()
    address=(body.get("address") or "").strip()
    notes=(body.get("notes") or "").strip()
    if not mode or not items or not name or not phone:
        raise HTTPException(status_code=400, detail="Faltan datos del pedido")
    # calculate total
    flat={i["id"]:i for i in menu_flat()}
    total=0.0
    for it in items:
        mid=it.get("id")
        qty=int(it.get("qty",1))
        if mid in flat:
            total += flat[mid]["precio"]*qty
    folio=_folio("PED")
    with _conn() as c:
        c.execute("INSERT INTO orders (folio,mode,items,total,name,phone,address,notes,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                  (folio,mode,json.dumps(items,ensure_ascii=False),round(total,2),name,phone,address,notes,datetime.utcnow().isoformat()))
    eta = "20-30 min" if mode in ("para llevar","a domicilio") else "servicio en mesa"
    return {"ok":True,"folio":folio,"total":round(total,2),"message":f"Pedido confirmado. Folio {folio}. Total ${total:,.2f} MXN. Tiempo estimado: {eta}."}

@app.post("/api/chat/public")
async def chat_public(request: Request):
    body=await request.json()
    message=(body.get("message") or "").strip()
    session_id=body.get("session_id") or ""
    if not message: raise HTTPException(status_code=400, detail="Mensaje vacío")
    info=public_info()
    context = SOULMD + "\n\nMENÚ:\n" + menu_text() + "\n\nINFO RESTAURANTE:\n" + json.dumps(info, ensure_ascii=False)
    if llm_client and llm_client.is_configured():
        msgs=[
            {"role":"system","content": context + "\n\nResponde solo con la respuesta final, sin razonamiento interno."},
            {"role":"user","content": message},
        ]
        reply=llm_client.chat(msgs, temperature=0.5, max_tokens=500)
        if reply:
            return {"reply":reply,"source":"openrouter","session_id":session_id}
    low=message.lower()
    if any(k in low for k in ["hora","horario","abren","cierran"]):
        reply=f"Nuestro horario es {info['hours']}. ¡Te esperamos!"
    elif any(k in low for k in ["ubicacion","ubicación","donde","dónde","dirección","direccion"]):
        reply=f"Estamos en {info['location']}. Contáctanos al {info['phone']} para la dirección exacta."
    elif any(k in low for k in ["reserva","reservar","mesa"]):
        reply="Para reservar, dime tu nombre, fecha, hora y número de personas y te aparto la mesa."
    elif any(k in low for k in ["pedido","orden","para llevar","domicilio"]):
        reply="Para hacer tu pedido, dime los platillos y cantidades, y si es para llevar, a domicilio o en mesa."
    elif any(k in low for k in ["telefono","teléfono","contacto","whatsapp"]):
        reply=f"Puedes llamarnos al {info['phone']} o escribir a {info['email']}."
    elif any(k in low for k in ["menu","menú","carta","platillo","comida","antojo"]):
        reply="Tenemos comida costera: ceviche, pescado a la talla, camarones al coco, arroz a la tumbada, tacos y más. ¿Qué se te antoja? Te recomiendo el pescado a la talla, ¡nuestro favorito!"
    elif any(k in low for k in ["recomienda","recomendación","sugerencia","qué me recomiendas"]):
        reply="Te recomiendo empezar con ceviche de pescado, seguir con pescado a la talla (¡nuestro favorito!) y cerrar con flan de coco. ¿Te lo aparto?"
    else:
        reply=("Soy el asistente de Puerto A&M. Puedo ayudarte con el menú, reservaciones, pedidos y recomendaciones. "
               "Escribe a "+info["email"]+" o "+info["phone"]+".")
    return {"reply":reply,"source":"local","session_id":session_id}

@app.get("/")
def index():
    return FileResponse(os.path.join(FRONTEND_DIR,"index.html"))

if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__=="__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
