-- Allow users to insert chunks for their own lessons
CREATE POLICY "Users can insert own chunks" ON public.lesson_chunks
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM lessons l
      JOIN courses c ON c.id = l.course_id
      WHERE l.id = lesson_chunks.lesson_id
      AND c.user_id = auth.uid()
    )
  );
