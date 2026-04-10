-- Migration 016: Metacognitive calibration
-- Adds confidence column to attempts for pre-submission self-assessment.
-- NULL = not rated (user skipped); 1 = guessing, 2 = unsure, 3 = confident
-- Evidence: metacognitive calibration g=0.57 (overconfidence is the biggest
-- predictor of poor learning; prediction + outcome comparison improves encoding)
ALTER TABLE public.attempts ADD COLUMN IF NOT EXISTS confidence SMALLINT NULL CHECK (confidence IN (1,2,3));
