-- Fix: restrict storage policies to user's own directory
-- Previously any authenticated user could read/write anyone's files

drop policy if exists "Users can upload course files" on storage.objects;
drop policy if exists "Users can read own course files" on storage.objects;
drop policy if exists "Users can delete own course files" on storage.objects;

-- Upload: only into own directory (path starts with user's ID)
create policy "Users can upload to own directory" on storage.objects
  for insert with check (
    bucket_id = 'course-files'
    and auth.uid() is not null
    and (storage.foldername(name))[1] = auth.uid()::text
  );

-- Read: only own files
create policy "Users can read own files" on storage.objects
  for select using (
    bucket_id = 'course-files'
    and auth.uid() is not null
    and (storage.foldername(name))[1] = auth.uid()::text
  );

-- Delete: only own files
create policy "Users can delete own files" on storage.objects
  for delete using (
    bucket_id = 'course-files'
    and auth.uid() is not null
    and (storage.foldername(name))[1] = auth.uid()::text
  );
