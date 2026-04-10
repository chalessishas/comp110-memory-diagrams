-- Migration 017: Misconceptions unique constraint
-- Enables upsert pattern (user_id, concept_id) so attempts POST can
-- increment occurrence_count on repeated wrong answers without duplicate rows.
ALTER TABLE public.misconceptions
  ADD CONSTRAINT misconceptions_user_concept_unique UNIQUE (user_id, concept_id);
