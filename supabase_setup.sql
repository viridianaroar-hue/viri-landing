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

-- (Opcional) Permitir acceso anónimo de solo inserción/lectura para la demo
alter table public.chat_messages enable row level security;
create policy "allow anon read" on public.chat_messages for select using (true);
create policy "allow anon insert" on public.chat_messages for insert with check (true);
