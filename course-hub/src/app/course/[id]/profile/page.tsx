import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { CourseTabs } from "@/components/CourseTabs";
import { ProfileView } from "@/components/ProfileView";

export default async function ProfilePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data: course } = await supabase.from("courses").select("title").eq("id", id).single();
  if (!course) redirect("/dashboard");

  // Get knowledge points
  const { data: kps } = await supabase
    .from("outline_nodes")
    .select("id, title")
    .eq("course_id", id)
    .eq("type", "knowledge_point");

  const kpIds = (kps ?? []).map(k => k.id);

  // Get mastery data
  const { data: mastery } = kpIds.length > 0
    ? await supabase.from("element_mastery").select("*").eq("user_id", user.id).in("concept_id", kpIds)
    : { data: [] };

  // Get misconceptions
  const { data: allMisconceptions } = kpIds.length > 0
    ? await supabase.from("misconceptions").select("*").eq("user_id", user.id).in("concept_id", kpIds).order("occurrence_count", { ascending: false })
    : { data: [] };

  // Get challenge logs for metacognition
  const { data: challenges } = kpIds.length > 0
    ? await supabase.from("challenge_logs").select("student_self_rating, ai_confidence_rating, meta_cognition_match").eq("user_id", user.id).in("concept_id", kpIds)
    : { data: [] };

  // Get study time (from attempts count this week)
  const weekAgo = new Date();
  weekAgo.setDate(weekAgo.getDate() - 7);
  const { data: recentAttempts } = await supabase
    .from("attempts")
    .select("id")
    .eq("user_id", user.id)
    .gte("answered_at", weekAgo.toISOString());

  const kpMap = new Map((kps ?? []).map(k => [k.id, k.title]));

  return (
    <div>
      <CourseTabs courseId={id} />
      <ProfileView
        courseTitle={course.title}
        totalKps={kpIds.length}
        mastery={(mastery ?? []).map(m => ({
          ...m,
          conceptTitle: kpMap.get(m.concept_id) ?? "Unknown",
        }))}
        misconceptions={allMisconceptions ?? []}
        metacognitionData={challenges ?? []}
        weeklyAttempts={(recentAttempts ?? []).length}
      />
    </div>
  );
}
