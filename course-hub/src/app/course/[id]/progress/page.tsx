import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { CourseTabs } from "@/components/CourseTabs";
import { ProgressGrid } from "@/components/ProgressGrid";
import { calculateMastery } from "@/lib/mastery";

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
    <div>
      <CourseTabs courseId={id} />
      <h2 className="text-lg font-medium mb-4">Knowledge Point Mastery</h2>
      <ProgressGrid data={data} />
    </div>
  );
}
