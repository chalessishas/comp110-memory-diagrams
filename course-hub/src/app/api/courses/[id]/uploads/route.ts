import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

export async function GET(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { data, error } = await supabase
    .from("uploads")
    .select("*")
    .eq("course_id", id)
    .order("created_at", { ascending: false });

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  // Generate signed download URLs for each file
  const withUrls = await Promise.all(
    (data ?? []).map(async (upload) => {
      // Extract storage path from file_url
      const pathMatch = upload.file_url.match(/course-files\/(.+)$/);
      if (pathMatch) {
        const { data: signed } = await supabase.storage
          .from("course-files")
          .createSignedUrl(pathMatch[1], 3600); // 1 hour
        return { ...upload, download_url: signed?.signedUrl ?? null };
      }
      return { ...upload, download_url: null };
    })
  );

  return NextResponse.json(withUrls);
}

export async function DELETE(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { data: course } = await supabase.from("courses").select("id").eq("id", id).eq("user_id", user.id).single();
  if (!course) return NextResponse.json({ error: "Not found" }, { status: 404 });

  const { upload_id } = await request.json();

  // Get file path, scoped to this course to prevent cross-course deletion
  const { data: upload } = await supabase.from("uploads").select("file_url").eq("id", upload_id).eq("course_id", id).single();
  if (upload) {
    const pathMatch = upload.file_url.match(/course-files\/(.+)$/);
    if (pathMatch) {
      await supabase.storage.from("course-files").remove([pathMatch[1]]);
    }
  }

  await supabase.from("uploads").delete().eq("id", upload_id).eq("course_id", id);
  return NextResponse.json({ success: true });
}
