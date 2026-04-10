-- Add unique constraint on fsrs_review_logs so that upsert with
-- onConflict: "user_id,question_id,reviewed_at" works correctly.
-- Without this constraint, the Supabase upsert silently inserts duplicates
-- on retry storms instead of being idempotent.

ALTER TABLE public.fsrs_review_logs
  ADD CONSTRAINT fsrs_review_logs_user_question_reviewed_at_key
  UNIQUE (user_id, question_id, reviewed_at);

-- Drop the plain index (superseded by the unique constraint which creates its own btree index)
DROP INDEX IF EXISTS idx_fsrs_review_logs_user_question;
