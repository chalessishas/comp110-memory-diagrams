import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { CourseTabs } from "@/components/CourseTabs";
import { KnowledgeTree } from "@/components/KnowledgeTree";
import { calculateMastery } from "@/lib/mastery";
import { T } from "@/components/T";

export default async function TreePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data: kps } = await supabase
    .from("outline_nodes")
    .select("id, title, content, parent_id, type")
    .eq("course_id", id)
    .order("order");

  const allNodes = kps ?? [];
  const knowledgePoints = allNodes.filter((n) => n.type === "knowledge_point");
  const nodeMap = new Map(allNodes.map((n) => [n.id, n]));

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

  const { data: lessons } = await supabase
    .from("lessons")
    .select("knowledge_point_id")
    .eq("course_id", id);
  const lessonKpIds = new Set((lessons ?? []).map((l) => l.knowledge_point_id));

  const kpQuestions = new Map<string, string[]>();
  for (const q of questions ?? []) {
    if (q.knowledge_point_id) {
      const list = kpQuestions.get(q.knowledge_point_id) ?? [];
      list.push(q.id);
      kpQuestions.set(q.knowledge_point_id, list);
    }
  }

  const treeNodes = knowledgePoints.map((kp) => {
    const qIds = kpQuestions.get(kp.id) ?? [];
    const kpAttempts = (attempts ?? []).filter((a) => qIds.includes(a.question_id));
    const mastery = calculateMastery(kpAttempts);
    const parent = kp.parent_id ? nodeMap.get(kp.parent_id) : null;

    return {
      id: kp.id,
      title: kp.title,
      mastery: mastery.level,
      rate: mastery.rate,
      totalAttempts: mastery.total,
      hasLesson: lessonKpIds.has(kp.id),
      parentTitle: parent?.title ?? null,
    };
  });

  return (
    <div>
      <CourseTabs courseId={id} />
      <div className="mb-6">
        <h2 className="text-xl font-semibold tracking-wide"><T k="tree.title" /></h2>
        <p className="text-sm mt-2">
          <T k="tree.desc" />
        </p>
      </div>
      <KnowledgeTree nodes={treeNodes} courseId={id} />
    </div>
  );
}
