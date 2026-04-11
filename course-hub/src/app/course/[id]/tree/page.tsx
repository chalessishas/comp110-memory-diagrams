import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { CourseTabs } from "@/components/CourseTabs";
import { KnowledgeTree } from "@/components/KnowledgeTree";
import type { MasteryLevel } from "@/types";
import { T } from "@/components/T";

const v2ToDisplay = (level: string | undefined): MasteryLevel => {
  if (!level || level === "unseen") return "untested";
  if (level === "exposed") return "weak";
  if (level === "practiced") return "reviewing";
  return "mastered"; // proficient or mastered
};

export default async function TreePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  // Parallel group 1: outline_nodes + lessons both need only course_id
  const [{ data: kps }, { data: lessons }] = await Promise.all([
    supabase
      .from("outline_nodes")
      .select("id, title, content, parent_id, type")
      .eq("course_id", id)
      .order("order"),
    supabase
      .from("lessons")
      .select("knowledge_point_id")
      .eq("course_id", id),
  ]);

  const allNodes = kps ?? [];
  const knowledgePoints = allNodes.filter((n) => n.type === "knowledge_point");
  const nodeMap = new Map(allNodes.map((n) => [n.id, n]));
  const kpIds = knowledgePoints.map((n) => n.id);
  const lessonKpIds = new Set((lessons ?? []).map((l) => l.knowledge_point_id));

  // Parallel group 2: element_mastery needs kpIds from group 1
  const { data: masteryRows } = kpIds.length > 0
    ? await supabase
        .from("element_mastery")
        .select("concept_id, current_level, times_tested, times_correct")
        .eq("user_id", user.id)
        .eq("element_name", "_overall")
        .in("concept_id", kpIds)
    : { data: [] };

  const masteryMap = new Map(
    (masteryRows ?? []).map((m) => [m.concept_id, m])
  );

  const treeNodes = knowledgePoints.map((kp) => {
    const m = masteryMap.get(kp.id);
    const parent = kp.parent_id ? nodeMap.get(kp.parent_id) : null;

    return {
      id: kp.id,
      title: kp.title,
      mastery: v2ToDisplay(m?.current_level),
      rate: m && m.times_tested > 0 ? m.times_correct / m.times_tested : 0,
      totalAttempts: m?.times_tested ?? 0,
      hasLesson: lessonKpIds.has(kp.id),
      parentTitle: parent?.title ?? null,
    };
  });

  return (
    <div>
      <CourseTabs courseId={id} />
      <div className="mb-6">
        <h2 className="text-xl font-semibold tracking-wide"><T k="tree.title" /></h2>
        <p className="text-sm mt-2" style={{ color: "var(--text-secondary)" }}>
          <T k="tree.desc" />
        </p>
      </div>
      <KnowledgeTree nodes={treeNodes} courseId={id} />
    </div>
  );
}
