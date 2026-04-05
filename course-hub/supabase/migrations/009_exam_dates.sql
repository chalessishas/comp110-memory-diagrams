create table public.exam_dates (
  id uuid primary key default gen_random_uuid(),
  course_id uuid not null references public.courses(id) on delete cascade,
  title text not null,
  exam_date date not null,
  knowledge_point_ids jsonb default '[]'::jsonb,
  created_at timestamptz not null default now()
);

create index idx_exam_dates_course on public.exam_dates(course_id);

alter table public.exam_dates enable row level security;
create policy "Users can CRUD own exam dates" on public.exam_dates
  for all using (
    exists (select 1 from public.courses where courses.id = exam_dates.course_id and courses.user_id = auth.uid())
  )
  with check (
    exists (select 1 from public.courses where courses.id = exam_dates.course_id and courses.user_id = auth.uid())
  );
