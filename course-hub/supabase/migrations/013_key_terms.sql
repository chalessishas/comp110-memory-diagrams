-- Add key_terms JSONB column to lesson_chunks for inline term explanations
-- Each entry: { "term": "Taylor series", "definition": "An infinite sum of terms..." }
ALTER TABLE public.lesson_chunks ADD COLUMN IF NOT EXISTS key_terms jsonb;

COMMENT ON COLUMN public.lesson_chunks.key_terms IS 'Array of {term, definition} objects for inline term tooltip cards';
