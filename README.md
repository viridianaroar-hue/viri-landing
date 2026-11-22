
## Memoria con Supabase (opcional)

1. Crea un proyecto en https://supabase.com/dashboard
2. Ejecuta `supabase_setup.sql` en el SQL Editor.
3. Configura en `.env`:
   - `SUPABASE_URL=https://xxxx.supabase.co`
   - `SUPABASE_KEY=tu_anon_key`
4. El chat guardará y recuperará el historial por `session_id`, dando memoria al agente.
