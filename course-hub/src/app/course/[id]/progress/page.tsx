import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import Link from "next/link";
import { CourseTabs } from "@/components/CourseTabs";
import { ProgressGrid } from "@/components/ProgressGrid";
import { StudyTrackerPanel } from "@/components/StudyTrackerPanel";
import { calculateMastery } from "@/lib/mastery";
import { ArrowLeft, Brain } from "lucide-react";

export default async function ProgressPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data: kps } = await supabase
    .from("outline_nodes")
    .select("*")
    .eq("course_id", id)
    .eq("type", "knowledge_point")
    .order("order");

  const { data: questions } = await supabase
    .from("questions")
    .select("id, knowledge_point_id")
    .eq("course_id", id);

  const questionIds = (questions ?? []).map((q) => q.id);
  const { data: attempts } = questionIds.length > 0
    ? await supabase
        .from("attempts")
        .select("question_id, is_correct, answered_at, confidence")
        .eq("user_id", user.id)
        .in("question_id", questionIds)
    : { data: [] };

  // Metacognitive calibration stats — accuracy grouped by confidence level
  const confStats = [1, 2, 3].map((lvl) => {
    const rated = (attempts ?? []).filter((a) => a.confidence === lvl);
    const correct = rated.filter((a) => a.is_correct).length;
    return { lvl, total: rated.length, correct, accuracy: rated.length > 0 ? correct / rated.length : null };
  });
  const totalRated = confStats.reduce((s, c) => s + c.total, 0);
  // Calibration quality: well-calibrated if accuracy increases with confidence
  const [c1, c2, c3] = confStats.map((s) => s.accuracy);
  const isCalibrated = c1 !== null && c2 !== null && c3 !== null && c1 <= c2 && c2 <= c3;
  const isOverconfident = c3 !== null && c1 !== null && c3 < c1;

  const kpQuestions = new Map<string, string[]>();
  for (const q of questions ?? []) {
    if (q.knowledge_point_id) {
      const list = kpQuestions.get(q.knowledge_point_id) ?? [];
      list.push(q.id);
      kpQuestions.set(q.knowledge_point_id, list);
    }
  }

  const data = (kps ?? []).map((kp) => {
    const qIds = kpQuestions.get(kp.id) ?? [];
    const kpAttempts = (attempts ?? []).filter((a) => qIds.includes(a.question_id));
    const mastery = calculateMastery(kpAttempts);
    return { node: kp, ...mastery };
  });

  return (
    <div className="space-y-8">
      <Link href="/dashboard" className="ui-button-ghost w-fit !px-0">
        <ArrowLeft size={14} />
        Back to Dashboard
      </Link>
      <CourseTabs courseId={id} />

      <div>
        <div className="ui-kicker mb-3">Progress</div>
        <h2 className="text-3xl font-semibold tracking-wide">See what is sticking.</h2>
        <p className="ui-copy mt-3 max-w-2xl">
          CourseHub groups your recent attempts into a quiet mastery map so the weak spots are easy to spot.
        </p>
      </div>

      <StudyTrackerPanel
        courseId={id}
        activeMode="studying"
        title="Progress Review Time"
        description="Time spent checking mastery and revisiting weak areas counts as study time. Long inactive stretches are marked as idle."
      />

      {totalRated >= 5 && (
        <div className="ui-panel p-5">
          <div className="flex items-center gap-2 mb-4">
            <Brain size={16} style={{ color: "var(--accent)" }} />
            <span className="text-sm font-medium">Confidence Calibration</span>
            {isCalibrated && (
              <span className="ml-auto text-xs px-2 py-0.5 rounded-lg font-medium" style={{ backgroundColor: "var(--success)", color: "white" }}>Well calibrated</span>
            )}
            {isOverconfident && (
              <span className="ml-auto text-xs px-2 py-0.5 rounded-lg font-medium" style={{ backgroundColor: "var(--warning)", color: "white" }}>Overconfident</span>
            )}
          </div>
          <div className="space-y-2.5">
            {confStats.map(({ lvl, total, accuracy }) => {
              const emoji = lvl === 1 ? "🤔" : lvl === 2 ? "🙂" : "😎";
              const label = lvl === 1 ? "Guessing" : lvl === 2 ? "Unsure" : "Confident";
              const pct = accuracy !== null ? Math.round(accuracy * 100) : null;
              const color = pct === null ? "var(--text-muted)"
                : pct >= 75 ? "var(--success)" : pct >= 50 ? "var(--warning)" : "var(--danger)";
              return (
                <div key={lvl} className="flex items-center gap-3">
                  <span className="w-5 text-center text-sm">{emoji}</span>
                  <span className="text-xs w-16" style={{ color: "var(--text-secondary)" }}>{label}</span>
                  <div className="flex-1 ui-progress-track">
                    <div className="ui-progress-bar" style={{ width: `${pct ?? 0}%`, backgroundColor: color }} />
                  </div>
                  <span className="text-xs w-20 text-right" style={{ color }}>
                    {pct !== null ? `${pct}% (${total})` : "—"}
                  </span>
                </div>
              );
            })}
          </div>
          <p className="text-[10px] mt-3" style={{ color: "var(--text-muted)" }}>
            Accuracy when you rated yourself as guessing, unsure, or confident. {totalRated} rated attempts.
          </p>
        </div>
      )}

      <ProgressGrid data={data} />
    </div>
  );
}
