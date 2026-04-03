-- Courses
create table public.courses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  description text,
  professor text,
  semester text,
  status text not null default 'active' check (status in ('active', 'archived')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_courses_user_id on public.courses(user_id);
create index idx_courses_status on public.courses(status);

alter table public.courses enable row level security;
create policy "Users can CRUD own courses" on public.courses
  for all using (user_id = auth.uid())
  with check (user_id = auth.uid());

-- Outline Nodes (adjacency list tree)
create table public.outline_nodes (
  id uuid primary key default gen_random_uuid(),
  course_id uuid not null references public.courses(id) on delete cascade,
  parent_id uuid references public.outline_nodes(id) on delete cascade,
  title text not null,
  type text not null check (type in ('week', 'chapter', 'topic', 'knowledge_point')),
  content text,
  "order" int not null default 0
);

create index idx_outline_course on public.outline_nodes(course_id);
create index idx_outline_parent on public.outline_nodes(parent_id);

alter table public.outline_nodes enable row level security;
create policy "Users can CRUD own outline nodes" on public.outline_nodes
  for all using (
    exists (select 1 from public.courses where courses.id = outline_nodes.course_id and courses.user_id = auth.uid())
  )
  with check (
    exists (select 1 from public.courses where courses.id = outline_nodes.course_id and courses.user_id = auth.uid())
  );

-- Uploads
create table public.uploads (
  id uuid primary key default gen_random_uuid(),
  course_id uuid not null references public.courses(id) on delete cascade,
  file_url text not null,
  file_name text not null,
  file_type text not null,
  upload_type text not null default 'other' check (upload_type in ('syllabus', 'exam', 'practice', 'notes', 'other')),
  parsed_content jsonb,
  status text not null default 'pending' check (status in ('pending', 'parsing', 'done', 'failed')),
  created_at timestamptz not null default now()
);

create index idx_uploads_course on public.uploads(course_id);

alter table public.uploads enable row level security;
create policy "Users can CRUD own uploads" on public.uploads
  for all using (
    exists (select 1 from public.courses where courses.id = uploads.course_id and courses.user_id = auth.uid())
  )
  with check (
    exists (select 1 from public.courses where courses.id = uploads.course_id and courses.user_id = auth.uid())
  );

-- Questions
create table public.questions (
  id uuid primary key default gen_random_uuid(),
  course_id uuid not null references public.courses(id) on delete cascade,
  source_upload_id uuid references public.uploads(id) on delete set null,
  knowledge_point_id uuid references public.outline_nodes(id) on delete set null,
  type text not null check (type in ('multiple_choice', 'fill_blank', 'short_answer', 'true_false')),
  stem text not null,
  options jsonb,
  answer text not null,
  explanation text,
  difficulty int not null default 3 check (difficulty between 1 and 5),
  created_at timestamptz not null default now()
);

create index idx_questions_course on public.questions(course_id);
create index idx_questions_kp on public.questions(knowledge_point_id);

alter table public.questions enable row level security;
create policy "Users can CRUD own questions" on public.questions
  for all using (
    exists (select 1 from public.courses where courses.id = questions.course_id and courses.user_id = auth.uid())
  )
  with check (
    exists (select 1 from public.courses where courses.id = questions.course_id and courses.user_id = auth.uid())
  );

-- Attempts
create table public.attempts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  question_id uuid not null references public.questions(id) on delete cascade,
  user_answer text not null,
  is_correct boolean not null,
  answered_at timestamptz not null default now()
);

create index idx_attempts_user on public.attempts(user_id);
create index idx_attempts_question on public.attempts(question_id);

alter table public.attempts enable row level security;
create policy "Users can CRUD own attempts" on public.attempts
  for all using (user_id = auth.uid())
  with check (user_id = auth.uid());

-- Storage bucket for uploads
insert into storage.buckets (id, name, public)
values ('course-files', 'course-files', false);

create policy "Users can upload course files" on storage.objects
  for insert with check (bucket_id = 'course-files' and auth.uid() is not null);

create policy "Users can read own course files" on storage.objects
  for select using (bucket_id = 'course-files' and auth.uid() is not null);

create policy "Users can delete own course files" on storage.objects
  for delete using (bucket_id = 'course-files' and auth.uid() is not null);

-- Updated_at trigger
create or replace function public.set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger courses_updated_at
  before update on public.courses
  for each row execute function public.set_updated_at();
