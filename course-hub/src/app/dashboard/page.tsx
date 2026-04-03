import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import Link from "next/link";
import { Plus, Archive } from "lucide-react";
import { CourseCard } from "@/components/CourseCard";

export default async function DashboardPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data: courses } = await supabase
    .from("courses")
    .select("*")
    .order("created_at", { ascending: false });

  const activeCourses = (courses ?? []).filter((c) => c.status === "active");
  const archivedCourses = (courses ?? []).filter((c) => c.status === "archived");

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-semibold">My Courses</h1>
        <Link
          href="/new-course"
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          style={{ backgroundColor: "var(--accent)", color: "white" }}
        >
          <Plus size={16} />
          New Course
        </Link>
      </div>

      {activeCourses.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-lg mb-2" style={{ color: "var(--text-secondary)" }}>No courses yet</p>
          <p className="mb-6" style={{ color: "var(--text-secondary)" }}>
            Upload a syllabus to get started
          </p>
          <Link
            href="/new-course"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg font-medium"
            style={{ backgroundColor: "var(--accent)", color: "white" }}
          >
            <Plus size={18} />
            Add Your First Course
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {activeCourses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      )}

      {archivedCourses.length > 0 && (
        <details className="mt-12">
          <summary className="flex items-center gap-2 cursor-pointer text-sm font-medium" style={{ color: "var(--text-secondary)" }}>
            <Archive size={16} />
            Archived ({archivedCourses.length})
          </summary>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4 opacity-60">
            {archivedCourses.map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        </details>
      )}
    </div>
  );
}
