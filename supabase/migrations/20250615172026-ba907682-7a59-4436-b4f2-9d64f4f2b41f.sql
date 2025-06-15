
alter table public.projects
  add column if not exists github_url text,
  add column if not exists demo_url text;
