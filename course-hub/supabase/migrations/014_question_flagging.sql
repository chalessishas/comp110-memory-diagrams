-- Question quality flagging: auto-detect or user-reported problematic questions
-- Flagged questions are hidden from practice/review but retained for analytics

ALTER TABLE public.questions
  ADD COLUMN flagged boolean NOT NULL DEFAULT false,
  ADD COLUMN flagged_reason text,
  ADD COLUMN flagged_at timestamptz;

CREATE INDEX idx_questions_flagged ON public.questions(course_id) WHERE flagged = true;
