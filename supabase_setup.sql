-- Ejecutar en el SQL Editor de Supabase
create table if not exists public.chat_messages (
  id uuid primary key default gen_random_uuid(),
  session_id text not null,
  role text not null check (role in ('user','assistant','system')),
  content text not null,
  created_at timestamptz not null default now()
);

-- Índice para consultas por sesión
create index if not exists idx_chat_messages_session on public.chat_messages(session_id, created_at);

-- Seguridad: SOLO el backend (clave secreta del servidor) accede a la tabla.
-- No crear políticas para anon: una política de lectura "using (true)" expone todas las conversaciones.
alter table public.chat_messages enable row level security;
revoke all on table public.chat_messages from anon, authenticated;
grant select, insert on table public.chat_messages to service_role;
