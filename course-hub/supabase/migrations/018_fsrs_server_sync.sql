-- Migration 018: Server-side FSRS card sync
-- Enables cross-device spaced repetition by persisting FSRS card state to Postgres.
-- Client still schedules locally (FSRS runs in-browser); this is the durable backup.
--
-- Pattern: client upserts card state after each review + appends review log row.
-- On first authenticated load for a course, client pulls DB state and merges with
-- localStorage (DB wins on conflict — server is source of truth for authenticated users).

CREATE TABLE public.fsrs_cards (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  question_id uuid NOT NULL REFERENCES public.questions(id) ON DELETE CASCADE,

  -- FSRS Card primitives (ts-fsrs Card interface)
  due timestamptz NOT NULL DEFAULT now(),
  stability float NOT NULL DEFAULT 0,
  difficulty float NOT NULL DEFAULT 0,
  elapsed_days int NOT NULL DEFAULT 0,
  scheduled_days int NOT NULL DEFAULT 0,
  reps int NOT NULL DEFAULT 0,
  lapses int NOT NULL DEFAULT 0,
  learning_steps int NOT NULL DEFAULT 0,
  state smallint NOT NULL DEFAULT 0, -- 0=New, 1=Learning, 2=Review, 3=Relearning
  last_review timestamptz,

  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),

  UNIQUE(user_id, question_id)
);

CREATE TABLE public.fsrs_review_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  question_id uuid NOT NULL REFERENCES public.questions(id) ON DELETE CASCADE,

  -- ts-fsrs ReviewLog fields (immutable — never updated, only appended)
  rating smallint NOT NULL,          -- 1=Again, 2=Hard, 3=Good, 4=Easy
  state smallint NOT NULL,
  due timestamptz NOT NULL,
  stability float NOT NULL,
  difficulty float NOT NULL,
  elapsed_days int NOT NULL,
  last_elapsed_days int NOT NULL,
  scheduled_days int NOT NULL,
  reviewed_at timestamptz NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX idx_fsrs_cards_user ON public.fsrs_cards(user_id);
CREATE INDEX idx_fsrs_cards_due ON public.fsrs_cards(user_id, due);
CREATE INDEX idx_fsrs_review_logs_user_question ON public.fsrs_review_logs(user_id, question_id);

-- RLS
ALTER TABLE public.fsrs_cards ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users manage own fsrs cards" ON public.fsrs_cards
  USING ((select auth.uid()) = user_id)
  WITH CHECK ((select auth.uid()) = user_id);

ALTER TABLE public.fsrs_review_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users manage own fsrs review logs" ON public.fsrs_review_logs
  USING ((select auth.uid()) = user_id)
  WITH CHECK ((select auth.uid()) = user_id);
