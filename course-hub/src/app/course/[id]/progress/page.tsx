import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import Link from "next/link";
import { CourseTabs } from "@/components/CourseTabs";
import { ProgressGrid } from "@/components/ProgressGrid";
import { StudyTrackerPanel } from "@/components/StudyTrackerPanel";
import { calculateMastery } from "@/lib/mastery";
import { ArrowLeft } from "lucide-react";

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
        .select("question_id, is_correct, answered_at")
        .eq("user_id", user.id)
        .in("question_id", questionIds)
    : { data: [] };

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
        <h2 className="text-3xl font-semibold">See what is sticking.</h2>
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

      <ProgressGrid data={data} />
    </div>
  );
}
