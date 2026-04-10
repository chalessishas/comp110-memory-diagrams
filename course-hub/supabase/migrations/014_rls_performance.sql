-- Migration 014: RLS Performance Optimization
-- Replace bare auth.uid() with (select auth.uid()) in all policies.
-- This allows Postgres to cache the result per statement rather than
-- re-evaluating auth.uid() on every row — measurable speedup on tables
-- with large row counts (element_mastery, attempts, questions).
--
-- Reference: https://supabase.com/docs/guides/troubleshooting/rls-performance-and-best-practices-Z5Jjwv

-- ── element_mastery ────────────────────────────────────────────────
DROP POLICY IF EXISTS "Users can manage own mastery" ON public.element_mastery;
CREATE POLICY "Users can manage own mastery" ON public.element_mastery
  FOR ALL USING (user_id = (select auth.uid()))
  WITH CHECK (user_id = (select auth.uid()));

-- ── misconceptions ──────────────────────────────────────────────────
DROP POLICY IF EXISTS "Users can manage own misconceptions" ON public.misconceptions;
CREATE POLICY "Users can manage own misconceptions" ON public.misconceptions
  FOR ALL USING (user_id = (select auth.uid()))
  WITH CHECK (user_id = (select auth.uid()));

-- ── challenge_logs ──────────────────────────────────────────────────
DROP POLICY IF EXISTS "Users can manage own challenge logs" ON public.challenge_logs;
CREATE POLICY "Users can manage own challenge logs" ON public.challenge_logs
  FOR ALL USING (user_id = (select auth.uid()))
  WITH CHECK (user_id = (select auth.uid()));

-- ── prerequisite_skips ──────────────────────────────────────────────
DROP POLICY IF EXISTS "Users can manage own prerequisite skips" ON public.prerequisite_skips;
CREATE POLICY "Users can manage own prerequisite skips" ON public.prerequisite_skips
  FOR ALL USING (user_id = (select auth.uid()))
  WITH CHECK (user_id = (select auth.uid()));

-- ── lesson_progress ─────────────────────────────────────────────────
DROP POLICY IF EXISTS "Users can manage own lesson progress" ON public.lesson_progress;
CREATE POLICY "Users can manage own lesson progress" ON public.lesson_progress
  FOR ALL USING (user_id = (select auth.uid()))
  WITH CHECK (user_id = (select auth.uid()));

-- ── question_bookmarks ──────────────────────────────────────────────
DROP POLICY IF EXISTS "Users can manage own bookmarks" ON public.question_bookmarks;
CREATE POLICY "Users can manage own bookmarks" ON public.question_bookmarks
  FOR ALL USING (user_id = (select auth.uid()))
  WITH CHECK (user_id = (select auth.uid()));

-- ── attempts ────────────────────────────────────────────────────────
DROP POLICY IF EXISTS "Users can CRUD own attempts" ON public.attempts;
CREATE POLICY "Users can CRUD own attempts" ON public.attempts
  FOR ALL USING (user_id = (select auth.uid()))
  WITH CHECK (user_id = (select auth.uid()));

-- ── courses ─────────────────────────────────────────────────────────
DROP POLICY IF EXISTS "Users can CRUD own courses" ON public.courses;
CREATE POLICY "Users can CRUD own courses" ON public.courses
  FOR ALL USING (user_id = (select auth.uid()))
  WITH CHECK (user_id = (select auth.uid()));

-- Note: EXISTS-subquery policies (outline_nodes, uploads, questions, etc.)
-- already benefit from the idx_courses_user_id index and the subquery acts
-- as a natural cache. No change needed for those.
