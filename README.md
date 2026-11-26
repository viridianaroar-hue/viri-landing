
## Memoria con Supabase (opcional)

1. Crea un proyecto en https://supabase.com/dashboard
2. Ejecuta `supabase_setup.sql` en el SQL Editor.
3. Configura en `.env`:
   - `SUPABASE_URL=https://xxxx.supabase.co`
   - `SUPABASE_SECRET_KEY=` la clave **secreta** del servidor (Settings › API Keys › Secret). Solo en el servidor: nunca en el frontend ni en el repositorio. La clave anon/publishable ya no tiene acceso a la tabla.
4. El chat guardará y recuperará el historial por `session_id`, dando memoria al agente.
