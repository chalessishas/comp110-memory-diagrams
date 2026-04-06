import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

export async function GET(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json([]);

  const { data: kps } = await supabase
    .from("outline_nodes")
    .select("id")
    .eq("course_id", id)
    .eq("type", "knowledge_point");

  const kpIds = (kps ?? []).map((k: { id: string }) => k.id);
  if (kpIds.length === 0) return NextResponse.json([]);

  const { data, error } = await supabase
    .from("element_mastery")
    .select("concept_id, current_level")
    .eq("user_id", user.id)
    .in("concept_id", kpIds);

  if (error) return NextResponse.json([]);
  return NextResponse.json(data);
}
