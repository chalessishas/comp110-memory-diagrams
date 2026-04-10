-- Drop duplicate RLS policies (redundant "CRUD" variants where "manage" variant exists with same condition)
-- Both used user_id = auth.uid(); the "manage" variants use the safer subquery form.
-- Keeping: "Users can manage own X" (SELECT auth.uid() subquery — avoids per-row re-evaluation)
-- Dropping: "Users can CRUD own X" (direct auth.uid() call)

DROP POLICY IF EXISTS "Users can CRUD own challenge logs" ON public.challenge_logs;
DROP POLICY IF EXISTS "Users can CRUD own mastery" ON public.element_mastery;
DROP POLICY IF EXISTS "Users can CRUD own progress" ON public.lesson_progress;
DROP POLICY IF EXISTS "Users can CRUD own misconceptions" ON public.misconceptions;
DROP POLICY IF EXISTS "Users can CRUD own prereq skips" ON public.prerequisite_skips;
DROP POLICY IF EXISTS "Users can CRUD own bookmarks" ON public.question_bookmarks;
