import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { reason } = await request.json();
  const validReasons = ["wrong_answer", "unclear", "too_easy", "too_hard", "duplicate", "irrelevant"];
  if (!validReasons.includes(reason)) {
    return NextResponse.json({ error: "Invalid reason" }, { status: 400 });
  }

  const { data, error } = await supabase
    .from("question_feedback")
    .upsert({ user_id: user.id, question_id: id, reason }, { onConflict: "user_id,question_id" })
    .select()
    .single();

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json(data);
}
