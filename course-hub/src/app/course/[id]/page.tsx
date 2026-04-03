import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { CourseTabs } from "@/components/CourseTabs";
import { OutlineTree } from "@/components/OutlineTree";
import { ArchiveButton } from "@/components/ArchiveButton";

export default async function CourseDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data: course } = await supabase.from("courses").select("*").eq("id", id).single();
  if (!course) redirect("/dashboard");

  const { data: outlineNodes } = await supabase
    .from("outline_nodes")
    .select("*")
    .eq("course_id", id)
    .order("order");

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-semibold">{course.title}</h1>
          {course.professor && (
            <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>{course.professor}</p>
          )}
          {course.semester && (
            <p className="text-xs mt-1" style={{ color: "var(--text-secondary)" }}>{course.semester}</p>
          )}
        </div>
        <ArchiveButton courseId={id} status={course.status} />
      </div>

      <CourseTabs courseId={id} />
      <OutlineTree nodes={outlineNodes ?? []} />
    </div>
  );
}
