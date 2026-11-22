# -*- coding: utf-8 -*-
import os, sys, json, sqlite3
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# load .env
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
# reuse llm_client from puerto-am? copy
app = FastAPI(title="Puerto A&M Landing", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
DB_PATH = os.path.join(BASE_DIR, "data", "app.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
def _conn():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c
with _conn() as c:
    c.execute("""CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, phone TEXT, message TEXT, source TEXT, created_at TEXT)""")

def _load_llm():
    # import local llm_client if present
    try:
        import llm_client
        return llm_client
    except Exception:
        return None
llm = _load_llm()

@app.get("/api/health")
def health():
    return {"status":"ok"}

@app.get("/api/public/info")
def public_info():
    return {"name":"Puerto A&M Gourmet","tagline":"Experiencia gastronómica con sabor a puerto","location":"Paraíso, Tabasco, México","phone":"(933) 688 55 85","email":"contacto@puertoamgourmet.mx","services":["Restaurante","Catering para eventos","Comedor industrial"],"hours":"Lun-Dom 8:00-22:00"}

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

@app.post("/api/chat/public")
async def chat_public(request: Request):
    body=await request.json()
    message=(body.get("message") or "").strip()
    session_id=body.get("session_id") or ""
    if not message: raise HTTPException(status_code=400, detail="Mensaje vacío")
    info=public_info()
    if llm and llm.is_configured():
        msgs=[
            {"role":"system","content":("Eres el asistente de atención al cliente de Puerto A&M Gourmet. Responde en español, amable y conciso. "
             "Info: "+json.dumps(info,ensure_ascii=False)+". Servicios: restaurante, catering, comedor industrial. Horario Lun-Dom 8:00-22:00. "
             "No inventes datos. Si preguntan por un pedido individual, ofrece seguimiento por teléfono/correo. "
             "Responde solo con la respuesta final, sin razonamiento.")},
            {"role":"user","content":message},
        ]
        reply=llm.chat(msgs, temperature=0.4, max_tokens=400)
        if reply:
            return {"reply":reply,"source":"openrouter","session_id":session_id}
    low=message.lower()
    if any(k in low for k in ["hora","horario","abren","cierran"]):
        reply=f"Nuestro horario es {info['hours']}. ¡Te esperamos!"
    elif any(k in low for k in ["ubicacion","ubicación","donde","dónde","dirección","direccion"]):
        reply=f"Estamos en {info['location']}. Contáctanos al {info['phone']} para la dirección exacta."
    elif any(k in low for k in ["telefono","teléfono","contacto","whatsapp"]):
        reply=f"Puedes llamarnos al {info['phone']} o escribir a {info['email']}."
    elif any(k in low for k in ["menu","menú","carta","platillo","comida"]):
        reply="La carta se actualiza por temporada. Solicita el menú vigente por WhatsApp o correo."
    elif any(k in low for k in ["reserva","reservar","mesa"]):
        reply="Para reservar, deja tus datos en el formulario de contacto o escríbenos por WhatsApp."
    elif any(k in low for k in ["catering","evento","boda","comedor industrial"]):
        reply="Ofrecemos catering para eventos y comedor industrial. Cuéntanos fecha, personas y tipo de evento."
    elif any(k in low for k in ["pedido","estatus","rastrear","seguimiento"]):
        reply=("No puedo rastrear pedidos en línea. Déjanos tu nombre, teléfono y número de pedido "
               "en el formulario o WhatsApp y te confirmamos el estatus.")
    else:
        reply=("Soy el asistente de Puerto A&M. Puedo ayudarte con horarios, ubicación, reservas, catering, menú y contacto. "
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
