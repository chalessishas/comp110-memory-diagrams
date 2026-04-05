import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

export async function GET(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { data: course } = await supabase.from("courses").select("title").eq("id", id).single();
  const { data: questions } = await supabase
    .from("questions")
    .select("stem, answer, explanation, type, options")
    .eq("course_id", id);

  if (!questions || questions.length === 0) {
    return NextResponse.json({ error: "No questions to export" }, { status: 400 });
  }

  // Generate Anki-importable tab-separated text
  // Format: front\tback\ttags
  const lines = questions.map((q) => {
    let front = q.stem;
    let back = q.answer;

    // For MC questions, include options in front
    if (q.type === "multiple_choice" && q.options) {
      const opts = (q.options as { label: string; text: string }[])
        .map((o) => `${o.label}. ${o.text}`)
        .join("<br>");
      front = `${q.stem}<br><br>${opts}`;
    }

    if (q.explanation) {
      back = `${q.answer}<br><br><i>${q.explanation}</i>`;
    }

    const tag = (course?.title ?? "CourseHub").replace(/\s+/g, "_");
    return `${front}\t${back}\t${tag}`;
  });

  const content = lines.join("\n");

  return new NextResponse(content, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Content-Disposition": `attachment; filename="${(course?.title ?? "coursehub").replace(/[^a-zA-Z0-9]/g, "_")}_anki.txt"`,
    },
  });
}
