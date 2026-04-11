import { createClient } from "@/lib/supabase/server";
import Link from "next/link";
import { Plus, Archive, LogIn, ClipboardPenLine, ShieldCheck, Sparkles } from "lucide-react";
import { CourseCard } from "@/components/CourseCard";
import { StudyTrackerPanel } from "@/components/StudyTrackerPanel";
import { StudyStatsCard } from "@/components/StudyStatsCard";
import { T } from "@/components/T";

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

  // Fetch question IDs per course for client-side due-count badges
  const courseIds = activeCourses.map((c) => c.id);
  const [questionsByCourseFetch, kpsByCourseFetch] = await Promise.all([
    courseIds.length > 0
      ? supabase.from("questions").select("id, course_id").in("course_id", courseIds)
      : Promise.resolve({ data: [] }),
    courseIds.length > 0
      ? supabase.from("outline_nodes").select("id, course_id").in("course_id", courseIds).eq("type", "knowledge_point")
      : Promise.resolve({ data: [] }),
  ]);

  const questionsByCourse: Record<string, string[]> = {};
  for (const q of questionsByCourseFetch.data ?? []) {
    if (!questionsByCourse[q.course_id]) questionsByCourse[q.course_id] = [];
    questionsByCourse[q.course_id].push(q.id);
  }

  // Batch mastery query — all KP ids across courses, then group
  const kpNodes = kpsByCourseFetch.data ?? [];
  const allKpIds = kpNodes.map((n) => n.id);
  const kpsByCourse: Record<string, string[]> = {};
  for (const n of kpNodes) {
    if (!kpsByCourse[n.course_id]) kpsByCourse[n.course_id] = [];
    kpsByCourse[n.course_id].push(n.id);
  }

  const masteryFetch = allKpIds.length > 0
    ? await supabase.from("element_mastery").select("concept_id, current_level").in("concept_id", allKpIds)
    : { data: [] };

  const LEARNED_LEVELS = new Set(["practiced", "proficient", "mastered"]);
  const masteryStatsByCourse: Record<string, { learned: number; total: number }> = {};
  for (const courseId of courseIds) {
    const kps = kpsByCourse[courseId] ?? [];
    const kpSet = new Set(kps);
    const learned = (masteryFetch.data ?? []).filter(
      (m) => kpSet.has(m.concept_id) && LEARNED_LEVELS.has(m.current_level)
    ).length;
    masteryStatsByCourse[courseId] = { learned, total: kps.length };
  }

  if (!user) {
    return (
      <div className="space-y-8">
        <div className="ui-panel p-6 md:p-8">
          <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
            <div>
              <div className="ui-kicker mb-4">CourseHub</div>
              <h1 className="text-4xl font-semibold tracking-tight"><T k="dashboard.guestTitle" /></h1>
              <p className="ui-copy mt-3 max-w-3xl">
                <T k="dashboard.guestDesc" />
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link href="/new-course" className="ui-button-primary">
                <ClipboardPenLine size={16} />
                <T k="dashboard.startGuest" />
              </Link>
              <Link href="/login" className="ui-button-secondary">
                <LogIn size={16} />
                <T k="nav.signIn" />
              </Link>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <div className="ui-panel p-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl mb-4" style={{ backgroundColor: "var(--bg-muted)" }}>
              <Sparkles size={20} />
            </div>
            <h2 className="text-lg font-semibold"><T k="dashboard.pasteAny" /></h2>
            <p className="ui-copy mt-2">
              <T k="dashboard.pasteDesc" />
            </p>
          </div>
          <div className="ui-panel p-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl mb-4" style={{ backgroundColor: "var(--bg-muted)" }}>
              <ShieldCheck size={20} />
            </div>
            <h2 className="text-lg font-semibold"><T k="dashboard.saveReady" /></h2>
            <p className="ui-copy mt-2">
              <T k="dashboard.saveDesc" />
            </p>
          </div>
          <div className="ui-panel p-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl mb-4" style={{ backgroundColor: "var(--bg-muted)" }}>
              <Plus size={20} />
            </div>
            <h2 className="text-lg font-semibold"><T k="dashboard.createAnytime" /></h2>
            <p className="ui-copy mt-2">
              <T k="dashboard.createDesc" />
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
          <div className="ui-kicker mb-4"><T k="dashboard.kicker" /></div>
          <h1 className="text-4xl font-semibold tracking-tight"><T k="dashboard.title" /></h1>
          <p className="ui-copy mt-3">
            <T k="dashboard.subtitle" />
          </p>
        </div>
        <Link
          href="/new-course"
          className="ui-button-primary"
        >
          <Plus size={16} />
          <T k="dashboard.newCourse" />
        </Link>
      </div>

      <StudyStatsCard />

      <StudyTrackerPanel
        track={false}
        className="mb-8"
      />

      {activeCourses.length === 0 ? (
        <div className="ui-empty">
          <p className="text-lg font-medium mb-2"><T k="dashboard.noCourses" /></p>
          <p className="mb-6" style={{ color: "var(--text-secondary)" }}>
            <T k="dashboard.uploadToStart" />
          </p>
          <Link
            href="/new-course"
            className="ui-button-primary"
          >
            <Plus size={18} />
            <T k="dashboard.addFirst" />
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
          {activeCourses.map((course) => (
            <CourseCard key={course.id} course={course} questionIds={questionsByCourse[course.id] ?? []} masteryStats={masteryStatsByCourse[course.id]} />
          ))}
        </div>
      )}

      {archivedCourses.length > 0 && (
        <details className="ui-panel mt-10 p-6">
          <summary className="flex items-center gap-3 cursor-pointer text-sm font-semibold list-none">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl" style={{ backgroundColor: "var(--bg-muted)" }}>
              <Archive size={16} />
            </div>
            <div>
              <span className="block"><T k="dashboard.archived" /></span>
              <span className="text-xs font-medium" style={{ color: "var(--text-secondary)" }}>
                {archivedCourses.length} <T k="dashboard.archivedCount" />
              </span>
            </div>
          </summary>
          <div className="grid grid-cols-1 gap-6 mt-5 md:grid-cols-2 xl:grid-cols-3 opacity-75">
            {archivedCourses.map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        </details>
      )}
    </div>
  );
}
