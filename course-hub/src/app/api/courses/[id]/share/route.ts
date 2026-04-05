import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

// Generate or get existing share link
export async function POST(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  // Check if token already exists
  const { data: existing } = await supabase
    .from("share_tokens")
    .select("token")
    .eq("course_id", id)
    .limit(1)
    .single();

  if (existing) return NextResponse.json({ token: existing.token });

  // Create new token
  const { data, error } = await supabase
    .from("share_tokens")
    .insert({ course_id: id })
    .select("token")
    .single();

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ token: data.token });
}

// Delete share link
export async function DELETE(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  await supabase.from("share_tokens").delete().eq("course_id", id);
  return NextResponse.json({ success: true });
}
