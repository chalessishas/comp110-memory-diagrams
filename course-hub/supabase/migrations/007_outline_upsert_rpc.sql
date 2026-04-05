CREATE OR REPLACE FUNCTION public.replace_outline(
  p_course_id uuid,
  p_nodes jsonb
) RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  node_count integer;
BEGIN
  -- Delete existing nodes (cascade will handle children)
  DELETE FROM public.outline_nodes WHERE course_id = p_course_id;

  -- Insert new nodes from JSON array
  INSERT INTO public.outline_nodes (id, course_id, parent_id, title, type, content, "order")
  SELECT
    (n->>'id')::uuid,
    p_course_id,
    NULLIF(n->>'parent_id', '')::uuid,
    n->>'title',
    n->>'type',
    n->>'content',
    (n->>'order')::integer
  FROM jsonb_array_elements(p_nodes) AS n;

  GET DIAGNOSTICS node_count = ROW_COUNT;
  RETURN node_count;
END;
$$;
