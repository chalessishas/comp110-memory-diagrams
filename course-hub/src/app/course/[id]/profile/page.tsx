import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { CourseTabs } from "@/components/CourseTabs";
import { ProfileView } from "@/components/ProfileView";

export default async function ProfilePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  // Parallel group 1: courses + outline_nodes + recentAttempts all independent
  const weekAgo = new Date();
  weekAgo.setDate(weekAgo.getDate() - 7);
  const [{ data: course }, { data: kps }, { data: recentAttempts }] = await Promise.all([
    supabase.from("courses").select("title").eq("id", id).single(),
    supabase.from("outline_nodes").select("id, title").eq("course_id", id).eq("type", "knowledge_point"),
    supabase.from("attempts").select("id").eq("user_id", user.id).gte("answered_at", weekAgo.toISOString()),
  ]);

  if (!course) redirect("/dashboard");

  const kpIds = (kps ?? []).map(k => k.id);

  // Parallel group 2: element_mastery + misconceptions + challenge_logs all need kpIds
  const [{ data: mastery }, { data: allMisconceptions }, { data: challenges }] = kpIds.length > 0
    ? await Promise.all([
        supabase.from("element_mastery").select("*").eq("user_id", user.id).eq("element_name", "_overall").in("concept_id", kpIds),
        supabase.from("misconceptions").select("*").eq("user_id", user.id).in("concept_id", kpIds).order("occurrence_count", { ascending: false }),
        supabase.from("challenge_logs").select("student_self_rating, ai_confidence_rating, meta_cognition_match").eq("user_id", user.id).in("concept_id", kpIds),
      ])
    : [{ data: null }, { data: null }, { data: null }];

  const kpMap = new Map((kps ?? []).map(k => [k.id, k.title]));

  return (
    <div className="space-y-6">
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
