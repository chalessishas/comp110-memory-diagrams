-- Share tokens for course sharing
create table public.share_tokens (
  id uuid primary key default gen_random_uuid(),
  course_id uuid not null references public.courses(id) on delete cascade,
  token text not null unique default encode(gen_random_bytes(16), 'hex'),
  created_at timestamptz not null default now()
);

create index idx_share_tokens_token on public.share_tokens(token);
create index idx_share_tokens_course on public.share_tokens(course_id);

alter table public.share_tokens enable row level security;

-- Owner can create/delete share tokens
create policy "Users can manage own share tokens" on public.share_tokens
  for all using (
    exists (select 1 from public.courses where courses.id = share_tokens.course_id and courses.user_id = auth.uid())
  )
  with check (
    exists (select 1 from public.courses where courses.id = share_tokens.course_id and courses.user_id = auth.uid())
  );

-- Anyone can read share tokens (needed for the fork flow)
create policy "Anyone can read share tokens" on public.share_tokens
  for select using (true);
