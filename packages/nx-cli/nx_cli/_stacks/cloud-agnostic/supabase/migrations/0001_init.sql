-- {{project_title}} — base schema.
-- Plain SQL: works on Supabase AND self-hosted PostgreSQL (cloud-agnostic).
-- No business logic — just a minimal, secure starting point.

create extension if not exists "pgcrypto";

-- A generic example table. Replace with your domain entities.
create table if not exists public.items (
    id          uuid primary key default gen_random_uuid(),
    owner_id    uuid not null,
    name        text not null,
    created_at  timestamptz not null default now()
);

create index if not exists items_owner_id_idx on public.items (owner_id);

-- Security by default: enable Row Level Security on every table.
alter table public.items enable row level security;

-- Policies are defined in policies.sql (kept separate so they can be reviewed
-- and re-applied independently). Until applied, RLS denies all access.
