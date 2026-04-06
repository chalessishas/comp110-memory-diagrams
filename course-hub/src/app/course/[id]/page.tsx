import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { CourseTabs } from "@/components/CourseTabs";
import { TodayView } from "@/components/TodayView";

export default async function CourseDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data: course } = await supabase.from("courses").select("*").eq("id", id).single();
  if (!course) redirect("/dashboard");

  // Get all knowledge points
  const { data: kps } = await supabase
    .from("outline_nodes")
    .select("id, title, type")
    .eq("course_id", id)
    .eq("type", "knowledge_point");

  // Get mastery data (guard empty array)
  const kpIds = (kps ?? []).map(k => k.id);
  const { data: mastery } = kpIds.length > 0
    ? await supabase.from("element_mastery").select("concept_id, current_level, fsrs_retrievability").eq("user_id", user.id).in("concept_id", kpIds)
    : { data: [] };

  // Get exam dates (future only)
  const { data: exams } = await supabase
    .from("exam_dates")
    .select("*")
    .eq("course_id", id)
    .gte("exam_date", new Date().toISOString().split("T")[0])
    .order("exam_date");

  // Get active misconceptions (guard empty array)
  const { data: misconceptions } = kpIds.length > 0
    ? await supabase.from("misconceptions").select("*").eq("user_id", user.id).in("concept_id", kpIds).eq("resolved", false)
    : { data: [] };

  // Get lessons to check what's been learned
  const { data: lessons } = await supabase
    .from("lessons")
    .select("id, knowledge_point_id")
    .eq("course_id", id);

  const lessonIds = (lessons ?? []).map(l => l.id);
  const { data: progress } = lessonIds.length > 0
    ? await supabase.from("lesson_progress").select("lesson_id, completed").eq("user_id", user.id).in("lesson_id", lessonIds)
    : { data: [] };

  const tasks = buildTodayTasks({
    kps: kps ?? [],
    mastery: mastery ?? [],
    exams: exams ?? [],
    misconceptions: misconceptions ?? [],
    lessons: lessons ?? [],
    progress: progress ?? [],
    courseTitle: course.title,
    courseId: id,
  });

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">{course.title}</h1>
        {course.professor && (
          <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>{course.professor}</p>
        )}
      </div>
      <CourseTabs courseId={id} />
      <TodayView tasks={tasks} courseId={id} />
    </div>
  );
}

// Priority sorting algorithm from the design doc
function buildTodayTasks(data: {
  kps: { id: string; title: string; type: string }[];
  mastery: { concept_id: string; current_level: string; fsrs_retrievability: number }[];
  exams: { id: string; title: string; exam_date: string }[];
  misconceptions: { id: string; concept_id: string; misconception_description: string; occurrence_count: number }[];
  lessons: { id: string; knowledge_point_id: string }[];
  progress: { lesson_id: string; completed: boolean }[];
  courseTitle: string;
  courseId: string;
}) {
  const tasks: Array<{
    id: string;
    type: string;
    priority: number;
    title: string;
    description: string;
    estimatedMinutes: number;
    count: number;
    color: string;
    courseId: string;
    courseTitle: string;
  }> = [];

  const masteryMap = new Map(data.mastery.map(m => [m.concept_id, m]));
  const completedLessons = new Set(data.progress.filter(p => p.completed).map(p => p.lesson_id));
  const now = new Date();

  // Priority 0+1: Exam urgent (≤3 days)
  for (const exam of data.exams) {
    const examDate = new Date(exam.exam_date + "T23:59:59");
    const daysUntil = Math.ceil((examDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

    if (daysUntil <= 3) {
      const activeMisconceptions = data.misconceptions;
      if (activeMisconceptions.length > 0) {
        tasks.push({
          id: `exam-review-${exam.id}`,
          type: "exam_review",
          priority: 1,
          title: `${exam.title} — Exam Review`,
          description: `${activeMisconceptions.length} weak spots need attention`,
          estimatedMinutes: activeMisconceptions.length * 8,
          count: activeMisconceptions.length,
          color: "var(--danger)",
          courseId: data.courseId,
          courseTitle: data.courseTitle,
        });
      }

      const unseenCount = data.kps.filter(kp => {
        const m = masteryMap.get(kp.id);
        return !m || m.current_level === "unseen";
      }).length;

      if (unseenCount > 0 && data.kps.length > 0 && unseenCount / data.kps.length >= 0.3) {
        tasks.push({
          id: `urgent-study-${exam.id}`,
          type: "urgent_study",
          priority: 0,
          title: `${exam.title} — Urgent Study`,
          description: `${unseenCount} knowledge points not yet learned`,
          estimatedMinutes: unseenCount * 6,
          count: unseenCount,
          color: "var(--danger)",
          courseId: data.courseId,
          courseTitle: data.courseTitle,
        });
      }
    } else if (daysUntil <= 14) {
      // Priority 3: Exam prep
      const weakCount = data.kps.filter(kp => {
        const m = masteryMap.get(kp.id);
        return !m || m.current_level === "unseen" || m.current_level === "exposed";
      }).length;

      if (weakCount > 0) {
        tasks.push({
          id: `exam-prep-${exam.id}`,
          type: "exam_prep",
          priority: 3,
          title: `${exam.title} — Study Plan`,
          description: `${weakCount} topics to strengthen before ${exam.title}`,
          estimatedMinutes: weakCount * 12,
          count: weakCount,
          color: "var(--warning)",
          courseId: data.courseId,
          courseTitle: data.courseTitle,
        });
      }
    }
  }

  // Priority 2: FSRS review (due cards)
  const dueForReview = data.mastery.filter(m =>
    m.fsrs_retrievability < 0.85 &&
    m.current_level !== "unseen"
  );

  if (dueForReview.length > 0) {
    tasks.push({
      id: "fsrs-review",
      type: "fsrs_review",
      priority: 2,
      title: `Review ${Math.min(dueForReview.length, 20)} knowledge points`,
      description: "Strengthen your memory before it fades",
      estimatedMinutes: Math.min(dueForReview.length, 20) * 1,
      count: Math.min(dueForReview.length, 20),
      color: "var(--warning)",
      courseId: data.courseId,
      courseTitle: data.courseTitle,
    });
  }

  // Priority 4: New content
  const lessonKpMap = new Map<string, string>();
  for (const l of data.lessons) {
    if (l.knowledge_point_id) lessonKpMap.set(l.knowledge_point_id, l.id);
  }

  const nextToLearn = data.kps.find(kp => {
    const lessonId = lessonKpMap.get(kp.id);
    if (!lessonId) return false;
    if (completedLessons.has(lessonId)) return false;
    const m = masteryMap.get(kp.id);
    return !m || m.current_level === "unseen";
  });

  if (nextToLearn) {
    tasks.push({
      id: `new-${nextToLearn.id}`,
      type: "new_content",
      priority: 4,
      title: nextToLearn.title,
      description: "Next lesson available",
      estimatedMinutes: 25,
      count: 1,
      color: "var(--accent)",
      courseId: data.courseId,
      courseTitle: data.courseTitle,
    });
  }

  // Priority 5: Weakness (recurring misconceptions)
  const persistentMisconceptions = data.misconceptions.filter(m => m.occurrence_count >= 3);
  if (persistentMisconceptions.length > 0) {
    tasks.push({
      id: "weakness",
      type: "weakness",
      priority: 5,
      title: "Strengthen weak spots",
      description: `${persistentMisconceptions.length} recurring issues to address`,
      estimatedMinutes: persistentMisconceptions.length * 5,
      count: persistentMisconceptions.length,
      color: "var(--accent)",
      courseId: data.courseId,
      courseTitle: data.courseTitle,
    });
  }

  tasks.sort((a, b) => a.priority - b.priority);

  return tasks;
}
