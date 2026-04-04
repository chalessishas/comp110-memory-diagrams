import { createClient } from "@/lib/supabase/server";
import Link from "next/link";
import { Plus, Archive, LogIn, ClipboardPenLine, ShieldCheck, Sparkles } from "lucide-react";
import { CourseCard } from "@/components/CourseCard";
import { StudyTrackerPanel } from "@/components/StudyTrackerPanel";

export default async function DashboardPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  const courses = user
    ? (await supabase
        .from("courses")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", { ascending: false })).data
    : [];

  const activeCourses = (courses ?? []).filter((c) => c.status === "active");
  const archivedCourses = (courses ?? []).filter((c) => c.status === "archived");

  if (!user) {
    return (
      <div className="space-y-8">
        <div className="ui-panel p-6 md:p-8">
          <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
            <div>
              <div className="ui-kicker mb-4">Guest Dashboard</div>
              <h1 className="text-4xl font-semibold tracking-tight">Try CourseHub before you commit.</h1>
              <p className="ui-copy mt-3 max-w-3xl">
                No account required to explore the flow. Paste a syllabus, preview the structure,
                and log in later only if you want to save it to your dashboard.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link href="/new-course" className="ui-button-primary">
                <ClipboardPenLine size={16} />
                Start as Guest
              </Link>
              <Link href="/login" className="ui-button-secondary">
                <LogIn size={16} />
                Sign In
              </Link>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="ui-panel p-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl mb-4" style={{ backgroundColor: "var(--bg-muted)", border: "1px solid var(--border)" }}>
              <Sparkles size={20} />
            </div>
            <h2 className="text-lg font-semibold">Paste text and preview fast</h2>
            <p className="ui-copy mt-2">
              Guests can paste course text directly and still get an outline preview right away.
            </p>
          </div>
          <div className="ui-panel p-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl mb-4" style={{ backgroundColor: "var(--bg-muted)", border: "1px solid var(--border)" }}>
              <ShieldCheck size={20} />
            </div>
            <h2 className="text-lg font-semibold">Login only when it matters</h2>
            <p className="ui-copy mt-2">
              Saving courses, syncing practice, and keeping long-term progress still happen behind sign-in.
            </p>
          </div>
          <div className="ui-panel p-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl mb-4" style={{ backgroundColor: "var(--bg-muted)", border: "1px solid var(--border)" }}>
              <Plus size={20} />
            </div>
            <h2 className="text-lg font-semibold">Upgrade from guest whenever you want</h2>
            <p className="ui-copy mt-2">
              The product stays usable without making account creation the very first step.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between mb-8">
        <div>
          <div className="ui-kicker mb-4">Dashboard</div>
          <h1 className="text-4xl font-semibold tracking-tight">My Courses</h1>
          <p className="ui-copy mt-3">
            Keep your semester quiet, organized, and easy to revisit.
          </p>
        </div>
        <Link
          href="/new-course"
          className="ui-button-primary"
        >
          <Plus size={16} />
          New Course
        </Link>
      </div>

      <StudyTrackerPanel
        title="Today"
        description="A local breakdown of how much time went into solving, reviewing, studying, or just sitting idle today."
        track={false}
        className="mb-8"
      />

      {activeCourses.length === 0 ? (
        <div className="ui-empty">
          <p className="text-lg font-medium mb-2">No courses yet</p>
          <p className="mb-6" style={{ color: "var(--text-secondary)" }}>
            Upload a syllabus to get started
          </p>
          <Link
            href="/new-course"
            className="ui-button-primary"
          >
            <Plus size={18} />
            Add Your First Course
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {activeCourses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      )}

      {archivedCourses.length > 0 && (
        <details className="ui-panel mt-10 p-6">
          <summary className="flex items-center gap-3 cursor-pointer text-sm font-semibold list-none">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl" style={{ backgroundColor: "var(--bg-muted)", border: "1px solid var(--border)" }}>
              <Archive size={16} />
            </div>
            <div>
              <span className="block">Archived Courses</span>
              <span className="text-xs font-medium" style={{ color: "var(--text-secondary)" }}>
                {archivedCourses.length} tucked away for later
              </span>
            </div>
          </summary>
          <div className="grid grid-cols-1 gap-4 mt-5 md:grid-cols-2 xl:grid-cols-3 opacity-75">
            {archivedCourses.map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        </details>
      )}
    </div>
  );
}
