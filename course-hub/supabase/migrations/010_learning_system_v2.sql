-- =====================================================
-- CourseHub Learning System V2 — Core Tables
-- Based on the revised design document
-- =====================================================

-- 1. Element Mastery (finest-grain mastery tracking per knowledge element)
CREATE TABLE public.element_mastery (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  concept_id uuid NOT NULL REFERENCES public.outline_nodes(id) ON DELETE CASCADE,
  element_name text NOT NULL,

  -- Cumulative stats
  times_tested int DEFAULT 0,
  times_correct int DEFAULT 0,
  times_non_mcq int DEFAULT 0,
  times_non_mcq_correct int DEFAULT 0,

  -- FSRS params (synced from ts-fsrs client state)
  fsrs_stability float DEFAULT 0,
  fsrs_difficulty float DEFAULT 5.0,
  fsrs_retrievability float DEFAULT 1.0,
  fsrs_last_review timestamptz,

  -- Current level
  current_level text DEFAULT 'unseen'
    CHECK (current_level IN ('unseen', 'exposed', 'practiced', 'proficient', 'mastered')),
  level_reached_at timestamptz DEFAULT now(),

  -- Response time tracking
  avg_response_time_ms float DEFAULT 0,

  -- Cross-concept tracking
  has_external_practice boolean DEFAULT false,
  has_non_mcq_correct boolean DEFAULT false,
  has_cross_concept_correct boolean DEFAULT false,
  has_transfer_correct boolean DEFAULT false,
  has_teaching_challenge_pass boolean DEFAULT false,
  first_contact_at timestamptz DEFAULT now(),

  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),

  UNIQUE(user_id, concept_id, element_name)
);

CREATE INDEX idx_mastery_user_concept ON public.element_mastery(user_id, concept_id);
CREATE INDEX idx_mastery_level ON public.element_mastery(current_level);

ALTER TABLE public.element_mastery ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can CRUD own mastery" ON public.element_mastery
  FOR ALL USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- 2. Misconceptions (AI-detected learning errors, tracked over time)
CREATE TABLE public.misconceptions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  concept_id uuid NOT NULL REFERENCES public.outline_nodes(id) ON DELETE CASCADE,

  misconception_description text NOT NULL,

  -- Timeline
  first_seen_at timestamptz DEFAULT now(),
  last_seen_at timestamptz DEFAULT now(),
  occurrence_count int DEFAULT 1,

  -- Resolution
  resolved boolean DEFAULT false,
  resolved_at timestamptz,
  relapsed boolean DEFAULT false,
  relapse_count int DEFAULT 0,

  -- Cross-concept tracking
  related_concepts uuid[] DEFAULT '{}',

  created_at timestamptz DEFAULT now()
);

CREATE INDEX idx_misconceptions_user ON public.misconceptions(user_id);
CREATE INDEX idx_misconceptions_active
  ON public.misconceptions(user_id) WHERE resolved = false;
CREATE INDEX idx_misconceptions_concept ON public.misconceptions(concept_id);

ALTER TABLE public.misconceptions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can CRUD own misconceptions" ON public.misconceptions
  FOR ALL USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- 3. Challenge Logs (AI questioning session records)
CREATE TABLE public.challenge_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  concept_id uuid NOT NULL REFERENCES public.outline_nodes(id) ON DELETE CASCADE,
  session_type text NOT NULL
    CHECK (session_type IN ('teaching_challenge', 'checkpoint_open', 'study_buddy', 'review')),

  -- AI turns
  turns jsonb NOT NULL DEFAULT '[]',

  -- Final result
  final_confidence text
    CHECK (final_confidence IN ('none', 'surface', 'partial', 'solid', 'mastery')),
  elements_passed text[] DEFAULT '{}',
  elements_failed text[] DEFAULT '{}',
  misconceptions_found text[] DEFAULT '{}',

  -- Metacognition
  student_self_rating int CHECK (student_self_rating BETWEEN 1 AND 5),
  ai_confidence_rating text,
  meta_cognition_match boolean,

  created_at timestamptz DEFAULT now()
);

CREATE INDEX idx_challenge_user ON public.challenge_logs(user_id);
CREATE INDEX idx_challenge_concept ON public.challenge_logs(concept_id);

ALTER TABLE public.challenge_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can CRUD own challenge logs" ON public.challenge_logs
  FOR ALL USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- 4. Prerequisite Skips (track when students skip prereqs + outcomes)
CREATE TABLE public.prerequisite_skips (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  concept_id uuid NOT NULL REFERENCES public.outline_nodes(id) ON DELETE CASCADE,
  skipped_prereq_id uuid NOT NULL REFERENCES public.outline_nodes(id) ON DELETE CASCADE,
  subsequent_accuracy float,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX idx_prereq_skips_user ON public.prerequisite_skips(user_id);

ALTER TABLE public.prerequisite_skips ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can CRUD own prereq skips" ON public.prerequisite_skips
  FOR ALL USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- 5. Lesson Chunks (replace monolithic lessons with chunk-checkpoint structure)
CREATE TABLE public.lesson_chunks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lesson_id uuid NOT NULL REFERENCES public.lessons(id) ON DELETE CASCADE,
  chunk_index int NOT NULL,

  -- Content
  content text NOT NULL, -- markdown
  widget_code text, -- optional React code for interactive canvas
  widget_description text,
  widget_challenge text,

  -- Checkpoint
  checkpoint_type text
    CHECK (checkpoint_type IN ('mcq', 'code', 'latex', 'open', 'canvas', 'ordering')),
  checkpoint_prompt text,
  checkpoint_answer text, -- correct answer or expected output
  checkpoint_options jsonb, -- for MCQ
  checkpoint_core_elements text[], -- elements being tested

  -- Remediation
  remediation_content text, -- shown if checkpoint fails
  remediation_question text, -- variant question
  remediation_answer text,

  created_at timestamptz DEFAULT now()
);

CREATE INDEX idx_chunks_lesson ON public.lesson_chunks(lesson_id, chunk_index);

ALTER TABLE public.lesson_chunks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can read own chunks" ON public.lesson_chunks
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.lessons l
      JOIN public.courses c ON c.id = l.course_id
      WHERE l.id = lesson_chunks.lesson_id AND c.user_id = auth.uid()
    )
  );

-- 6. Lesson Progress (track where user left off in each lesson)
CREATE TABLE public.lesson_progress (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  lesson_id uuid NOT NULL REFERENCES public.lessons(id) ON DELETE CASCADE,
  last_chunk_index int DEFAULT 0,
  completed boolean DEFAULT false,
  checkpoint_results jsonb DEFAULT '{}', -- {chunk_index: {passed: bool, attempts: int}}
  started_at timestamptz DEFAULT now(),
  completed_at timestamptz,

  UNIQUE(user_id, lesson_id)
);

CREATE INDEX idx_lesson_progress_user ON public.lesson_progress(user_id);

ALTER TABLE public.lesson_progress ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can CRUD own progress" ON public.lesson_progress
  FOR ALL USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- 7. Add core_elements to outline_nodes for mastery tracking
ALTER TABLE public.outline_nodes
  ADD COLUMN IF NOT EXISTS core_elements text[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS prerequisites uuid[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS prerequisite_type text DEFAULT 'soft'
    CHECK (prerequisite_type IN ('hard', 'soft'));

-- 8. Updated_at triggers
CREATE OR REPLACE FUNCTION public.set_updated_at_v2()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER element_mastery_updated_at
  BEFORE UPDATE ON public.element_mastery
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_v2();
