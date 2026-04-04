-- Question bookmarks (personal question bank across courses)
create table public.question_bookmarks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  question_id uuid not null references public.questions(id) on delete cascade,
  note text,
  created_at timestamptz not null default now(),
  unique(user_id, question_id)
);

create index idx_bookmarks_user on public.question_bookmarks(user_id);

alter table public.question_bookmarks enable row level security;
create policy "Users can CRUD own bookmarks" on public.question_bookmarks
  for all using (user_id = auth.uid())
  with check (user_id = auth.uid());
