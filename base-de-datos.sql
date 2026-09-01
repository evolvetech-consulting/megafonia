-- Pegá esto en Supabase → SQL Editor → Run.
-- Crea las dos tablas y deja los permisos listos.

-- 1. El planning: una sola fila con todo adentro.
create table if not exists planning (
  id           int primary key default 1,
  datos        jsonb not null default '{}'::jsonb,
  actualizado  timestamptz not null default now(),
  constraint una_sola_fila check (id = 1)
);
insert into planning (id, datos) values (1, '{}'::jsonb)
  on conflict (id) do nothing;

-- 2. Los avisos de "no puedo" que deja el equipo desde el enlace.
create table if not exists avisos (
  id      bigserial primary key,
  equipo  text not null,
  persona text not null,
  dia     int  not null,
  mes     text not null,
  nota    text,
  visto   boolean not null default false,
  creado  timestamptz not null default now()
);

-- 3. Permisos: cualquiera con el enlace puede leer el planning y dejar avisos.
alter table planning enable row level security;
alter table avisos   enable row level security;

drop policy if exists planning_lectura on planning;
create policy planning_lectura on planning for select using (true);

drop policy if exists planning_escritura on planning;
create policy planning_escritura on planning for update using (true) with check (true);

drop policy if exists avisos_lectura on avisos;
create policy avisos_lectura on avisos for select using (true);

drop policy if exists avisos_alta on avisos;
create policy avisos_alta on avisos for insert with check (true);

drop policy if exists avisos_marcar on avisos;
create policy avisos_marcar on avisos for update using (true) with check (true);

drop policy if exists avisos_borrar on avisos;
create policy avisos_borrar on avisos for delete using (true);
