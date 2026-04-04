-- Course Notes (voice or typed notes organized by AI)
create table public.course_notes (
  id uuid primary key default gen_random_uuid(),
  course_id uuid not null references public.courses(id) on delete cascade,
  knowledge_point_id uuid references public.outline_nodes(id) on delete set null,
  source text not null default 'voice' check (source in ('voice', 'text')),
  raw_transcript text not null,
  title text not null,
  summary text not null,
  key_points jsonb not null default '[]'::jsonb,
  confusing_points jsonb not null default '[]'::jsonb,
  next_action text,
  clarification_questions jsonb not null default '[]'::jsonb,
  clarification_answers jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);

create index idx_course_notes_course on public.course_notes(course_id);
create index idx_course_notes_kp on public.course_notes(knowledge_point_id);
create index idx_course_notes_created_at on public.course_notes(created_at desc);

alter table public.course_notes enable row level security;
create policy "Users can CRUD own course notes" on public.course_notes
  for all using (
    exists (select 1 from public.courses where courses.id = course_notes.course_id and courses.user_id = auth.uid())
  )
  with check (
    exists (select 1 from public.courses where courses.id = course_notes.course_id and courses.user_id = auth.uid())
  );
