import Link from "next/link";
import { redirect } from "next/navigation";
import { ArrowLeft, Mic, NotebookPen } from "lucide-react";
import { createClient } from "@/lib/supabase/server";
import { CourseTabs } from "@/components/CourseTabs";
import { StudyTrackerPanel } from "@/components/StudyTrackerPanel";
import { VoiceNotesPanel } from "@/components/VoiceNotesPanel";
import { toCourseNote, type CourseNoteRow } from "@/lib/course-notes";

export default async function CourseNotesPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data: course } = await supabase
    .from("courses")
    .select("*")
    .eq("id", id)
    .eq("user_id", user.id)
    .single();

  if (!course) redirect("/dashboard");

  const { data: outlineNodes } = await supabase
    .from("outline_nodes")
    .select("id, title, type")
    .eq("course_id", id)
    .order("order");

  const { data: noteRows } = await supabase
    .from("course_notes")
    .select("*")
    .eq("course_id", id)
    .order("created_at", { ascending: false });

  const knowledgePoints = (outlineNodes ?? []).filter((node) => node.type === "knowledge_point");
  const fallbackTargets = knowledgePoints.length > 0 ? knowledgePoints : outlineNodes ?? [];
  const nodeTitleById = new Map((outlineNodes ?? []).map((node) => [node.id, node.title]));
  const notes = (noteRows ?? []).map((row) =>
    toCourseNote(row as CourseNoteRow, row.knowledge_point_id ? nodeTitleById.get(row.knowledge_point_id) ?? null : null)
  );

  return (
    <div className="space-y-8">
      <Link href="/dashboard" className="ui-button-ghost w-fit !px-0">
        <ArrowLeft size={14} />
        Back to Dashboard
      </Link>

      <div className="ui-panel p-6 md:p-8">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <div className="ui-kicker mb-4">Notes</div>
            <h1 className="text-4xl font-semibold tracking-wide">Talk your way into clearer notes.</h1>
            <p className="ui-copy mt-3 max-w-3xl">
              CourseHub captures your spoken understanding, cleans it up, and pushes back when the explanation is still vague.
            </p>
            <div className="flex flex-wrap gap-2 mt-5">
              <span className="ui-badge">
                <Mic size={12} />
                Voice-first
              </span>
              <span className="ui-badge">
                <NotebookPen size={12} />
                {notes.length} saved notes
              </span>
              <span className="ui-badge">{fallbackTargets.length} knowledge points</span>
            </div>
          </div>
        </div>
      </div>

      <CourseTabs courseId={id} />

      <StudyTrackerPanel
        courseId={id}
        activeMode="studying"
      />

      <VoiceNotesPanel
        courseId={id}
        knowledgePoints={fallbackTargets.map((item) => ({ id: item.id, title: item.title }))}
        initialNotes={notes}
      />
    </div>
  );
}
