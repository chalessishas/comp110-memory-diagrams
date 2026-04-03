import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const formData = await request.formData();
  const file = formData.get("file") as File;
  const courseId = formData.get("courseId") as string | null;

  if (!file) return NextResponse.json({ error: "No file provided" }, { status: 400 });

  const timestamp = Date.now();
  const safeName = file.name.replace(/[^a-zA-Z0-9._-]/g, "_");
  const path = `${user.id}/${timestamp}_${safeName}`;

  const { error: uploadError } = await supabase.storage
    .from("course-files")
    .upload(path, file);

  if (uploadError) return NextResponse.json({ error: uploadError.message }, { status: 500 });

  const { data: { publicUrl } } = supabase.storage.from("course-files").getPublicUrl(path);

  const ext = file.name.split(".").pop()?.toLowerCase() ?? "";
  const fileType = ["pdf"].includes(ext) ? "pdf"
    : ["ppt", "pptx"].includes(ext) ? "ppt"
    : ["png", "jpg", "jpeg", "webp"].includes(ext) ? "image"
    : ["txt", "md", "docx"].includes(ext) ? "text"
    : "other";

  if (courseId) {
    const { data: upload, error: dbError } = await supabase
      .from("uploads")
      .insert({
        course_id: courseId,
        file_url: publicUrl,
        file_name: file.name,
        file_type: fileType,
        status: "pending",
      })
      .select()
      .single();

    if (dbError) return NextResponse.json({ error: dbError.message }, { status: 500 });
    return NextResponse.json({ upload, storagePath: path });
  }

  return NextResponse.json({ storagePath: path, fileUrl: publicUrl, fileName: file.name, fileType });
}
