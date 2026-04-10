import { createClient } from "@/lib/supabase/server";
import { checkRateLimit } from "@/lib/rate-limit";
import { NextResponse } from "next/server";

// GET /api/courses/[id]/mastery-summary?since=ISO_TIMESTAMP
// Returns knowledge points that leveled up since the given timestamp
export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json([]);

  if (!await checkRateLimit(`mastery-summary:${user.id}`, 20, 60_000)) {
    return NextResponse.json({ error: "Rate limit exceeded" }, { status: 429 });
  }

  const since = new URL(request.url).searchParams.get("since");
  if (!since) return NextResponse.json({ error: "since param required" }, { status: 400 });

  // Get all KP IDs for this course
  const { data: kps } = await supabase
    .from("outline_nodes")
    .select("id")
    .eq("course_id", id)
    .eq("type", "knowledge_point");

  const kpIds = (kps ?? []).map((k: { id: string }) => k.id);
  if (kpIds.length === 0) return NextResponse.json([]);

  // Find _overall mastery records that leveled up since the given timestamp,
  // joined with outline_nodes for the human-readable concept title
  const { data, error } = await supabase
    .from("element_mastery")
    .select("concept_id, current_level, level_reached_at, outline_nodes!concept_id(title)")
    .eq("user_id", user.id)
    .eq("element_name", "_overall")
    .in("concept_id", kpIds)
    .neq("current_level", "unseen")
    .gte("level_reached_at", since)
    .order("level_reached_at", { ascending: false });

  if (error) return NextResponse.json([]);

  // Flatten join result: return element_name as the concept title
  const result = (data ?? []).map((m) => ({
    element_name: (m.outline_nodes as unknown as { title: string } | null)?.title ?? "Knowledge point",
    current_level: m.current_level,
    level_reached_at: m.level_reached_at,
  }));

  return NextResponse.json(result);
}
