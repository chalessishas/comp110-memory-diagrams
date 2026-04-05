create table public.question_feedback (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  question_id uuid not null references public.questions(id) on delete cascade,
  reason text not null check (reason in ('wrong_answer', 'unclear', 'too_easy', 'too_hard', 'duplicate', 'irrelevant')),
  created_at timestamptz not null default now(),
  unique(user_id, question_id)
);

create index idx_question_feedback_question on public.question_feedback(question_id);

alter table public.question_feedback enable row level security;
create policy "Users can CRUD own feedback" on public.question_feedback
  for all using (user_id = auth.uid())
  with check (user_id = auth.uid());
