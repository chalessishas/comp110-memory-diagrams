import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import Link from "next/link";
import { CourseTabs } from "@/components/CourseTabs";
import { ProgressGrid } from "@/components/ProgressGrid";
import { StudyTrackerPanel } from "@/components/StudyTrackerPanel";
import type { MasteryLevel } from "@/types";
import { ArrowLeft } from "lucide-react";
import { CalibrationPanel } from "@/components/CalibrationPanel";
import { T } from "@/components/T";

export default async function ProgressPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  // Parallel group 1: both queries use course_id directly, no inter-dependency
  const [{ data: kps }, { data: questions }] = await Promise.all([
    supabase
      .from("outline_nodes")
      .select("*")
      .eq("course_id", id)
      .eq("type", "knowledge_point")
      .order("order"),
    supabase
      .from("questions")
      .select("id, knowledge_point_id")
      .eq("course_id", id),
  ]);

  const kpIds = (kps ?? []).map((kp) => kp.id);
  const questionIds = (questions ?? []).map((q) => q.id);

  // Parallel group 2: attempts depends on questionIds, masteryRows depends on kpIds
  const [{ data: attempts }, { data: masteryRows }] = await Promise.all([
    questionIds.length > 0
      ? supabase
          .from("attempts")
          .select("question_id, is_correct, answered_at, confidence")
          .eq("user_id", user.id)
          .in("question_id", questionIds)
      : Promise.resolve({ data: [] as { question_id: string; is_correct: boolean; answered_at: string; confidence: number | null }[] }),
    kpIds.length > 0
      ? supabase
          .from("element_mastery")
          .select("concept_id, current_level, times_tested, times_correct")
          .eq("user_id", user.id)
          .in("concept_id", kpIds)
      : Promise.resolve({ data: [] as { concept_id: string; current_level: string; times_tested: number; times_correct: number }[] }),
  ]);

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

  const masteryMap = new Map(
    (masteryRows ?? []).map((m) => [m.concept_id, m])
  );

  // Map mastery-v2 5-level to ProgressGrid 4-level display categories
  const v2ToDisplay = (level: string | undefined): MasteryLevel => {
    if (!level || level === "unseen") return "untested";
    if (level === "exposed") return "weak";
    if (level === "practiced") return "reviewing";
    return "mastered"; // proficient or mastered
  };

  const data = (kps ?? []).map((kp) => {
    const m = masteryMap.get(kp.id);
    const level = v2ToDisplay(m?.current_level);
    const total = m?.times_tested ?? 0;
    const rate = total > 0 ? (m?.times_correct ?? 0) / total : 0;
    return { node: kp, level, rate, total };
  });


  return (
    <div className="space-y-8">
      <Link href="/dashboard" className="ui-button-ghost w-fit !px-0">
        <ArrowLeft size={14} />
        <T k="misc.backToDashboard" />
      </Link>
      <CourseTabs courseId={id} />

      <div>
        <div className="ui-kicker mb-3"><T k="progress.kicker" /></div>
        <h2 className="text-3xl font-semibold tracking-wide"><T k="progress.tagline" /></h2>
        <p className="ui-copy mt-3 max-w-2xl">
          <T k="progress.intro" />
        </p>
      </div>

      <StudyTrackerPanel
        courseId={id}
        activeMode="studying"
      />

      {totalRated >= 5 && (
        <CalibrationPanel
          confStats={confStats}
          totalRated={totalRated}
          isCalibrated={isCalibrated}
          isOverconfident={isOverconfident}
        />
      )}

      <ProgressGrid data={data} />
    </div>
  );
}
