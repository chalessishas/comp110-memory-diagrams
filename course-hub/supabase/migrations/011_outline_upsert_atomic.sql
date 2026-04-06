-- Atomic outline upsert: delete + insert in a single transaction
-- Uses SECURITY INVOKER so RLS is checked against the calling user (not function owner)
create or replace function public.upsert_outline_nodes(
  p_course_id uuid,
  p_nodes jsonb
) returns int
language plpgsql
security invoker
as $$
declare
  node_count int;
begin
  -- Delete existing nodes for this course
  delete from public.outline_nodes where course_id = p_course_id;

  -- Insert new nodes
  insert into public.outline_nodes (id, course_id, parent_id, title, type, content, "order")
  select
    (node->>'id')::uuid,
    p_course_id,
    (node->>'parent_id')::uuid,
    node->>'title',
    node->>'type',
    node->>'content',
    (node->>'order')::int
  from jsonb_array_elements(p_nodes) as node;

  get diagnostics node_count = row_count;

  -- Touch updated_at on the course
  update public.courses set updated_at = now() where id = p_course_id;

  return node_count;
end;
$$;
