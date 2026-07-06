-- backend schema setup for Supabase (Postgres + pgvector)
-- Run in Supabase SQL editor.

-- Extensions
create extension if not exists "pgcrypto";
create extension if not exists "vector";

-- =========================
-- skill_profiles
-- =========================
create table if not exists public.skill_profiles (
    skill_id        uuid primary key default gen_random_uuid(),
    user_id         uuid not null unique,
    username        varchar(100) not null,
    email           varchar(255) not null,
    "current_role"  varchar(100),
    target_role     varchar(100),
    skills          jsonb not null default '{}'::jsonb,
    skill_gaps      jsonb not null default '[]'::jsonb,
    role_alignment  varchar(30),
    resume_path     varchar(500),
    status          varchar(30) not null default 'COMPLETED',
    created_at      timestamptz default now()
);

create index if not exists ix_skill_profiles_email
  on public.skill_profiles (email);

-- =========================
-- courses (includes embedding)
-- =========================
create table if not exists public.courses (
    course_id           uuid primary key default gen_random_uuid(),
    course_name         varchar(255) not null,
    provider            varchar(100),
    external_course_id  varchar(100),
    description         text,
    category            varchar(100),
    difficulty_level    varchar(20),
    duration_hours      numeric(6, 2),
    url                 varchar(500),
    prerequisites       jsonb not null default '[]'::jsonb,
    skills_taught       jsonb not null default '[]'::jsonb,
    rating              numeric(3, 2),
    enrollment_count    integer default 0,
    embedding           vector(768),
    created_at          timestamptz default now()
);

create index if not exists ix_courses_external_course_id
  on public.courses (external_course_id);

-- If courses table already existed without embedding, add it.
alter table public.courses
  add column if not exists embedding vector(768);

-- Vector similarity index (cosine distance)
-- Note: for ivfflat to be effective, you typically need data before meaningful performance gains.
create index if not exists ix_courses_embedding
  on public.courses
  using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

-- RPC: match_courses
create or replace function public.match_courses(
    query_embedding vector(768),
    match_count int default 10
)
returns setof public.courses
language sql stable
as $$
    select *
    from public.courses
    where embedding is not null
    order by embedding <=> query_embedding
    limit match_count;
$$;

-- =========================
-- roadmaps
-- =========================
create table if not exists public.roadmaps (
    roadmap_id        uuid primary key default gen_random_uuid(),
    user_id           uuid not null,
    skill_profile_id  uuid references public.skill_profiles (skill_id),
    target_role       varchar(100),
    status            varchar(20) not null default 'active',
    hours_per_week    integer,
    learning_rate     varchar(20),
    total_courses     integer default 0,
    created_at        timestamptz default now(),
    updated_at        timestamptz default now()
);

create index if not exists ix_roadmaps_user_id
  on public.roadmaps (user_id);

-- =========================
-- roadmap_courses
-- =========================
create table if not exists public.roadmap_courses (
    id                      uuid primary key default gen_random_uuid(),
    roadmap_id              uuid not null references public.roadmaps (roadmap_id),
    course_id               uuid not null references public.courses (course_id),
    sequence_order          integer not null default 0,
    month                   integer,
    status                  varchar(20) not null default 'not_started',
    completion_percentage   integer not null default 0,
    quiz_score              integer,
    hours_spent             numeric(5, 2) default 0,
    notes                   text
);