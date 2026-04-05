create table public.lessons (
  id uuid primary key default gen_random_uuid(),
  course_id uuid not null references public.courses(id) on delete cascade,
  knowledge_point_id uuid not null references public.outline_nodes(id) on delete cascade,
  title text not null,
  content text not null,
  key_takeaways jsonb not null default '[]'::jsonb,
  examples jsonb not null default '[]'::jsonb,
  "order" int not null default 0,
  created_at timestamptz not null default now()
);

create index idx_lessons_course on public.lessons(course_id);
create index idx_lessons_kp on public.lessons(knowledge_point_id);

alter table public.lessons enable row level security;
create policy "Users can CRUD own lessons" on public.lessons
  for all using (
    exists (select 1 from public.courses where courses.id = lessons.course_id and courses.user_id = auth.uid())
  )
  with check (
    exists (select 1 from public.courses where courses.id = lessons.course_id and courses.user_id = auth.uid())
  );
