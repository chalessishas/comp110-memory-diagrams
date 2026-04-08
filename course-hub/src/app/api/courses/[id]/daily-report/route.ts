import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

export const maxDuration = 55;

interface DayStats {
  date: string;
  attempted: number;
  correct: number;
  lessonsCompleted: number;
}

export interface DailyReportData {
  today: {
    attempted: number;
    correct: number;
    accuracy: number;
    lessonsCompleted: number;
    lessonsStarted: number;
    levelUps: { conceptId: string; conceptTitle: string; from: string; to: string }[];
    newMisconceptions: number;
    resolvedMisconceptions: number;
  };
  weekHistory: DayStats[];
  mastery: {
    total: number;
    unseen: number;
    exposed: number;
    practiced: number;
    proficient: number;
    mastered: number;
  };
  troubleSpots: { conceptId: string; conceptTitle: string; attempted: number; correct: number }[];
}

interface KpRow { id: string; title: string }
interface QuestionRow { id: string; knowledge_point_id: string | null }
interface AttemptRow { question_id: string; is_correct: boolean; answered_at: string }
interface ProgressRow { lesson_id: string; completed: boolean; started_at: string; completed_at: string | null }
interface MasteryRow { concept_id: string; current_level: string; updated_at: string; level_reached_at: string }
interface MisconceptionRow { concept_id: string; created_at: string; resolved: boolean; resolved_at: string | null }

export async function GET(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { data: course } = await supabase.from("courses").select("id").eq("id", id).single();
  if (!course) return NextResponse.json({ error: "Not found" }, { status: 404 });

  const { data: kps } = await supabase
    .from("outline_nodes")
    .select("id, title")
    .eq("course_id", id)
    .eq("type", "knowledge_point");

  const kpList = (kps ?? []) as KpRow[];
  const kpIds = kpList.map((k: KpRow) => k.id);
  const kpMap = new Map(kpList.map((k: KpRow) => [k.id, k.title]));

  const now = new Date();
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).toISOString();
  const weekAgo = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 6).toISOString();

  const { data: questions } = await supabase
    .from("questions")
    .select("id, knowledge_point_id")
    .eq("course_id", id);

  const qList = (questions ?? []) as QuestionRow[];
  const questionIds = qList.map((q: QuestionRow) => q.id);
  const qToKp = new Map(qList.map((q: QuestionRow) => [q.id, q.knowledge_point_id]));

  const { data: attempts } = questionIds.length > 0
    ? await supabase
        .from("attempts")
        .select("question_id, is_correct, answered_at")
        .eq("user_id", user.id)
        .in("question_id", questionIds)
        .gte("answered_at", weekAgo)
        .order("answered_at")
    : { data: [] as AttemptRow[] };

  const { data: lessons } = await supabase
    .from("lessons")
    .select("id, knowledge_point_id")
    .eq("course_id", id);

  const lessonIds = ((lessons ?? []) as { id: string }[]).map((l: { id: string }) => l.id);
  const { data: progress } = lessonIds.length > 0
    ? await supabase
        .from("lesson_progress")
        .select("lesson_id, completed, started_at, completed_at")
        .eq("user_id", user.id)
        .in("lesson_id", lessonIds)
    : { data: [] as ProgressRow[] };

  const { data: mastery } = kpIds.length > 0
    ? await supabase
        .from("element_mastery")
        .select("concept_id, current_level, updated_at, level_reached_at")
        .eq("user_id", user.id)
        .in("concept_id", kpIds)
    : { data: [] as MasteryRow[] };

  const { data: misconceptions } = kpIds.length > 0
    ? await supabase
        .from("misconceptions")
        .select("concept_id, created_at, resolved, resolved_at")
        .eq("user_id", user.id)
        .in("concept_id", kpIds)
    : { data: [] as MisconceptionRow[] };

  // ─── Aggregate Today ───

  const attemptList = (attempts ?? []) as AttemptRow[];
  const progressList = (progress ?? []) as ProgressRow[];
  const masteryList = (mastery ?? []) as MasteryRow[];
  const miscList = (misconceptions ?? []) as MisconceptionRow[];

  const todayAttempts = attemptList.filter((a: AttemptRow) => a.answered_at >= todayStart);
  const todayCorrect = todayAttempts.filter((a: AttemptRow) => a.is_correct).length;

  const todayLessonsCompleted = progressList.filter(
    (p: ProgressRow) => p.completed && p.completed_at && p.completed_at >= todayStart
  ).length;

  const todayLessonsStarted = progressList.filter(
    (p: ProgressRow) => p.started_at >= todayStart
  ).length;

  const levelUps = masteryList
    .filter((m: MasteryRow) => m.level_reached_at >= todayStart && m.current_level !== "unseen")
    .map((m: MasteryRow) => ({
      conceptId: m.concept_id,
      conceptTitle: kpMap.get(m.concept_id) ?? "Unknown",
      from: inferPreviousLevel(m.current_level),
      to: m.current_level,
    }));

  const newMisconceptions = miscList.filter(
    (m: MisconceptionRow) => m.created_at >= todayStart
  ).length;

  const resolvedMisconceptions = miscList.filter(
    (m: MisconceptionRow) => m.resolved && m.resolved_at && m.resolved_at >= todayStart
  ).length;

  // ─── 7-Day History ───

  const weekHistory: DayStats[] = [];
  for (let i = 6; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth(), now.getDate() - i);
    const dayStart = d.toISOString();
    const dayEnd = new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1).toISOString();
    const dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

    const dayAttempts = attemptList.filter((a: AttemptRow) => a.answered_at >= dayStart && a.answered_at < dayEnd);
    const dayCompleted = progressList.filter(
      (p: ProgressRow) => p.completed && p.completed_at && p.completed_at >= dayStart && p.completed_at < dayEnd
    ).length;

    weekHistory.push({
      date: dateStr,
      attempted: dayAttempts.length,
      correct: dayAttempts.filter((a: AttemptRow) => a.is_correct).length,
      lessonsCompleted: dayCompleted,
    });
  }

  // ─── Mastery Distribution ───

  const masteryDist = {
    total: kpIds.length,
    unseen: 0,
    exposed: 0,
    practiced: 0,
    proficient: 0,
    mastered: 0,
  };

  const masteryMap = new Map(masteryList.map((m: MasteryRow) => [m.concept_id, m.current_level]));
  for (const kpId of kpIds) {
    const level = masteryMap.get(kpId) ?? "unseen";
    masteryDist[level as keyof typeof masteryDist] =
      (masteryDist[level as keyof typeof masteryDist] as number) + 1;
  }

  // ─── Trouble Spots ───

  const kpAccuracy = new Map<string, { attempted: number; correct: number }>();
  for (const a of todayAttempts) {
    const kpId = qToKp.get(a.question_id);
    if (!kpId) continue;
    const cur = kpAccuracy.get(kpId) ?? { attempted: 0, correct: 0 };
    cur.attempted++;
    if (a.is_correct) cur.correct++;
    kpAccuracy.set(kpId, cur);
  }

  const troubleSpots: DailyReportData["troubleSpots"] = Array.from(kpAccuracy.entries())
    .filter(([, v]) => v.attempted >= 2 && v.correct / v.attempted < 0.6)
    .sort((a, b) => (a[1].correct / a[1].attempted) - (b[1].correct / b[1].attempted))
    .slice(0, 5)
    .map(([kpId, v]) => ({
      conceptId: kpId,
      conceptTitle: kpMap.get(kpId) ?? "Unknown",
      attempted: v.attempted,
      correct: v.correct,
    }));

  const result: DailyReportData = {
    today: {
      attempted: todayAttempts.length,
      correct: todayCorrect,
      accuracy: todayAttempts.length > 0 ? Math.round((todayCorrect / todayAttempts.length) * 100) : 0,
      lessonsCompleted: todayLessonsCompleted,
      lessonsStarted: todayLessonsStarted,
      levelUps,
      newMisconceptions,
      resolvedMisconceptions,
    },
    weekHistory,
    mastery: masteryDist,
    troubleSpots,
  };

  return NextResponse.json(result);
}

function inferPreviousLevel(current: string): string {
  const levels = ["unseen", "exposed", "practiced", "proficient", "mastered"];
  const idx = levels.indexOf(current);
  return idx > 0 ? levels[idx - 1] : "unseen";
}
