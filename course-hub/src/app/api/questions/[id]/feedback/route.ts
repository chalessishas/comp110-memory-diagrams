import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

const AUTO_FLAG_THRESHOLD = 2; // flag after N independent "wrong_answer" reports

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

  // Auto-flag: if "wrong_answer" reports reach threshold, flag the question immediately
  if (reason === "wrong_answer") {
    const { count } = await supabase
      .from("question_feedback")
      .select("id", { count: "exact", head: true })
      .eq("question_id", id)
      .eq("reason", "wrong_answer");

    if (count && count >= AUTO_FLAG_THRESHOLD) {
      await supabase
        .from("questions")
        .update({
          flagged: true,
          flagged_reason: `${count} users reported wrong answer`,
          flagged_at: new Date().toISOString(),
        })
        .eq("id", id)
        .eq("flagged", false); // idempotent: only flag if not already flagged
    }
  }

  return NextResponse.json({ ...data, auto_flagged: reason === "wrong_answer" });
}
