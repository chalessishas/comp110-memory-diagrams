-- Partial index for mastery-summary API query pattern:
-- GET /api/courses/[id]/mastery-summary?since=ISO
-- Filters: user_id + level_reached_at >= since + current_level != 'unseen'
-- Without this, large element_mastery tables require a seq scan on user_id match.
CREATE INDEX IF NOT EXISTS idx_element_mastery_user_level_reached
  ON public.element_mastery (user_id, level_reached_at DESC)
  WHERE current_level != 'unseen';
