import { createClient } from "@/lib/supabase/server";
import { parseSyllabus, parseSyllabusText, parseExamQuestions } from "@/lib/ai";
import { checkRateLimit } from "@/lib/rate-limit";
import { NextResponse } from "next/server";

export const maxDuration = 60;

export async function POST(request: Request) {
  // All parse paths require auth — AI calls cost money
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const ip = user.id;
  if (!checkRateLimit(ip, 10, 60_000)) {
    return NextResponse.json({ error: "Rate limit exceeded. Try again in a minute." }, { status: 429 });
  }

  const { storagePath, rawText, parseType, courseId, language } = await request.json();

  if ((parseType === "syllabus" || !parseType) && typeof rawText === "string" && rawText.trim().length > 0) {
    try {
      // Truncate very long text to avoid timeout (keep first 6000 chars which covers course structure)
      const trimmed = rawText.trim();
      const text = trimmed.length > 6000 ? trimmed.slice(0, 6000) + "\n\n[Remaining content truncated for processing]" : trimmed;
      const result = await parseSyllabusText(text, language);
      return NextResponse.json({ type: "syllabus", data: result });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      return NextResponse.json({ error: `Failed to parse syllabus: ${message}` }, { status: 500 });
    }
  }

  if (!storagePath) {
    return NextResponse.json({ error: "storagePath or rawText required" }, { status: 400 });
  }

  const { data: fileData, error: downloadError } = await supabase.storage
    .from("course-files")
    .download(storagePath);

  if (downloadError || !fileData) {
    return NextResponse.json({ error: "Failed to download file" }, { status: 500 });
  }

  const buffer = Buffer.from(await fileData.arrayBuffer());
  const base64 = buffer.toString("base64");
  const ext = storagePath.split(".").pop()?.toLowerCase() ?? "";
  const mimeType = ext === "pdf" ? "application/pdf"
    : ["png"].includes(ext) ? "image/png"
    : ["jpg", "jpeg"].includes(ext) ? "image/jpeg"
    : "application/pdf";

  try {
    if (parseType === "syllabus" || !parseType) {
      const result = await parseSyllabus(base64, mimeType, language);
      return NextResponse.json({ type: "syllabus", data: result });
    }

    if (parseType === "exam") {
      let knowledgePoints: { id: string; title: string }[] = [];

      if (courseId) {
        const { data: nodes } = await supabase
          .from("outline_nodes")
          .select("id, title")
          .eq("course_id", courseId)
          .eq("type", "knowledge_point");
        knowledgePoints = nodes ?? [];
      }

      const questions = await parseExamQuestions(base64, mimeType, knowledgePoints);
      return NextResponse.json({ type: "exam", data: questions });
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: `AI parsing failed: ${message}` }, { status: 500 });
  }

  return NextResponse.json({ error: "Invalid parseType" }, { status: 400 });
}
