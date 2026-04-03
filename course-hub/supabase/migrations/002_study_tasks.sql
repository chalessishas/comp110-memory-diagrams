-- Study Tasks (auto-generated from outline)
create table public.study_tasks (
  id uuid primary key default gen_random_uuid(),
  course_id uuid not null references public.courses(id) on delete cascade,
  knowledge_point_id uuid references public.outline_nodes(id) on delete set null,
  title text not null,
  description text not null,
  task_type text not null check (task_type in ('read', 'practice', 'review')),
  priority int not null default 2 check (priority between 1 and 3),
  status text not null default 'todo' check (status in ('todo', 'done')),
  "order" int not null default 0,
  created_at timestamptz not null default now()
);

create index idx_study_tasks_course on public.study_tasks(course_id);
create index idx_study_tasks_kp on public.study_tasks(knowledge_point_id);

alter table public.study_tasks enable row level security;
create policy "Users can CRUD own study tasks" on public.study_tasks
  for all using (
    exists (select 1 from public.courses where courses.id = study_tasks.course_id and courses.user_id = auth.uid())
  )
  with check (
    exists (select 1 from public.courses where courses.id = study_tasks.course_id and courses.user_id = auth.uid())
  );
