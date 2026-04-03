import { createClient } from "@/lib/supabase/server";
import { parseSyllabus, parseExamQuestions } from "@/lib/ai";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { storagePath, parseType, courseId } = await request.json();
  if (!storagePath) return NextResponse.json({ error: "storagePath required" }, { status: 400 });

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

  if (parseType === "syllabus" || !parseType) {
    const result = await parseSyllabus(base64, mimeType);
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

  return NextResponse.json({ error: "Invalid parseType" }, { status: 400 });
}
