import type { SupabaseClient } from "@supabase/supabase-js";

/** Returns true if the given course belongs to the user. */
export async function verifyCourseOwnership(
  supabase: SupabaseClient,
  courseId: string,
  userId: string,
): Promise<boolean> {
  const { data } = await supabase
    .from("courses")
    .select("id")
    .eq("id", courseId)
    .eq("user_id", userId)
    .single();
  return !!data;
}

/**
 * Returns true if the given outline_node belongs to a course owned by the user.
 * Requires two queries: node → course → user_id.
 */
export async function verifyNodeOwnership(
  supabase: SupabaseClient,
  nodeId: string,
  userId: string,
): Promise<boolean> {
  const { data: node } = await supabase
    .from("outline_nodes")
    .select("course_id")
    .eq("id", nodeId)
    .single();
  if (!node) return false;
  return verifyCourseOwnership(supabase, node.course_id, userId);
}
