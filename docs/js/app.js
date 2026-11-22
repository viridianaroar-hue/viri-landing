const API = '';
const chatSession = 'pub-' + Math.random().toString(36).slice(2);

// Header scroll
const header = document.getElementById('siteHeader');
window.addEventListener('scroll', () => {
  header.classList.toggle('scrolled', window.scrollY > 20);
});

// Burger
const burger = document.getElementById('burger');
const navLinks = document.getElementById('navLinks');
if (burger) burger.addEventListener('click', () => navLinks.classList.toggle('open'));

// Reveal on scroll
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); } });
}, { threshold: 0.12 });
document.querySelectorAll('.reveal').forEach(el => io.observe(el));

// Contact form
const form = document.getElementById('contactForm');
if (form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    const payload = {
      name: fd.get('name'),
      email: fd.get('email'),
      phone: fd.get('phone'),
      message: fd.get('message'),
      source: 'landing'
    };
    const msg = document.getElementById('formMsg');
    try {
      const r = await fetch('/api/leads', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
      if (!r.ok) throw new Error('error');
      msg.textContent = '¡Gracias! Tu solicitud fue enviada. Te contactaremos pronto.';
      form.reset();
    } catch {
      msg.textContent = 'No se pudo enviar. Intenta por teléfono o correo.';
    }
  });
}

// Chat widget
const fab = document.getElementById('chatFab');
const panel = document.getElementById('chatPanel');
const closeBtn = document.getElementById('chatClose');
const body = document.getElementById('chatBody');
const input = document.getElementById('chatInput');
const send = document.getElementById('chatSend');

function addMsg(text, who) {
  const wrap = document.createElement('div');
  wrap.className = 'chat-msg ' + who;
  const b = document.createElement('div');
  b.className = 'chat-bubble';
  b.textContent = text;
  wrap.appendChild(b);
  body.appendChild(wrap);
  body.scrollTop = body.scrollHeight;
}
function showTyping() {
  const wrap = document.createElement('div');
  wrap.className = 'chat-msg bot';
  wrap.id = 'typing';
  wrap.innerHTML = '<div class="chat-bubble"><div class="chat-typing"><span></span><span></span><span></span></div></div>';
  body.appendChild(wrap);
  body.scrollTop = body.scrollHeight;
}
function hideTyping() { const t = document.getElementById('typing'); if (t) t.remove(); }

async function sendMsg() {
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  addMsg(text, 'user');
  showTyping();
  try {
    const r = await fetch('/api/chat/public', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ message: text, session_id: chatSession }) });
    if (!r.ok) throw new Error('backend');
    const data = await r.json();
    hideTyping();
    addMsg(data.reply || 'Sin respuesta.', 'bot');
  } catch {
    hideTyping();
    addMsg('El chat en línea no está disponible en esta versión estática. Contáctanos al (933) 688 55 85 o contacto@puertoamgourmet.mx y con gusto te atendemos.', 'bot');
  }
}
if (fab) fab.addEventListener('click', () => { panel.classList.toggle('open'); if (panel.classList.contains('open') && body.childElementCount === 0) addMsg('¡Hola! Soy el asistente de Puerto A&M. ¿En qué puedo ayudarte? (horarios, reservas, catering, menú, contacto)', 'bot'); });
if (closeBtn) closeBtn.addEventListener('click', () => panel.classList.remove('open'));
if (send) send.addEventListener('click', sendMsg);
if (input) input.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendMsg(); });
