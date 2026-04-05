import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import Link from "next/link";
import { CourseTabs } from "@/components/CourseTabs";
import { OutlineTree } from "@/components/OutlineTree";
import { ArchiveButton } from "@/components/ArchiveButton";
import { ShareButton } from "@/components/ShareButton";
import { RegenerateButton } from "@/components/RegenerateButton";
import { StudyTaskList } from "@/components/StudyTaskList";
import { StudyTrackerPanel } from "@/components/StudyTrackerPanel";
import { LearningBlueprint } from "@/components/LearningBlueprint";
import { WrongAnswerNotebook } from "@/components/WrongAnswerNotebook";
import { VoiceNotesPanel } from "@/components/VoiceNotesPanel";
import { calculateMastery } from "@/lib/mastery";
import { toCourseNote, type CourseNoteRow } from "@/lib/course-notes";
import type { MasteryLevel, OutlineNode, StudyTask } from "@/types";
import { ArrowLeft, Download } from "lucide-react";
import { ExamCountdown } from "@/components/ExamCountdown";

type CourseAttempt = {
  question_id: string;
  is_correct: boolean;
  answered_at: string;
  user_answer: string;
};

function selectStudyTargets(nodes: OutlineNode[]) {
  const knowledgePoints = nodes.filter((node) => node.type === "knowledge_point");
  if (knowledgePoints.length > 0) return knowledgePoints;

  const parentIds = new Set(nodes.map((node) => node.parent_id).filter(Boolean));
  const leafNodes = nodes.filter((node) => !parentIds.has(node.id));
  if (leafNodes.length > 0) return leafNodes;

  return nodes;
}

function buildNextAction({
  title,
  nextTask,
  questionCount,
  masteryLevel,
  totalAttempts,
}: {
  title: string;
  nextTask?: StudyTask;
  questionCount: number;
  masteryLevel: MasteryLevel;
  totalAttempts: number;
}) {
  if (nextTask) {
    if (nextTask.task_type === "read") return `Start by learning "${title}": ${nextTask.title}.`;
    if (nextTask.task_type === "practice") return `Do reps on "${title}": ${nextTask.title}.`;
    return `Review "${title}" and close the gap: ${nextTask.title}.`;
  }

  if (questionCount > 0 && totalAttempts === 0) {
    return `Open practice and answer a few questions on "${title}" to measure your baseline.`;
  }

  if (questionCount > 0 && masteryLevel !== "mastered") {
    return `Redo the questions on "${title}" until you can explain the idea without looking at the answer.`;
  }

  return `Write a short summary of "${title}" in your own words, then move to the next point.`;
}

export default async function CourseDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data: course } = await supabase.from("courses").select("*").eq("id", id).single();
  if (!course) redirect("/dashboard");

  const { data: outlineNodes } = await supabase
    .from("outline_nodes")
    .select("*")
    .eq("course_id", id)
    .order("order");

  const { data: studyTasks } = await supabase
    .from("study_tasks")
    .select("*")
    .eq("course_id", id)
    .order("priority")
    .order("order");

  const { data: questions } = await supabase
    .from("questions")
    .select("id, knowledge_point_id, stem, answer, explanation")
    .eq("course_id", id);

  const { data: noteRows } = await supabase
    .from("course_notes")
    .select("*")
    .eq("course_id", id)
    .order("created_at", { ascending: false });

  const { data: exams } = await supabase
    .from("exam_dates")
    .select("*")
    .eq("course_id", id)
    .order("exam_date");

  const questionIds = (questions ?? []).map((question) => question.id);
  const { data: attempts } = questionIds.length > 0
    ? await supabase
        .from("attempts")
        .select("question_id, is_correct, answered_at, user_answer")
        .eq("user_id", user.id)
        .in("question_id", questionIds)
    : { data: [] as CourseAttempt[] };

  const nodeTitleById = new Map((outlineNodes ?? []).map((node) => [node.id, node.title]));
  const notes = (noteRows ?? []).map((row) =>
    toCourseNote(row as CourseNoteRow, row.knowledge_point_id ? nodeTitleById.get(row.knowledge_point_id) ?? null : null)
  );
  const studyTargets = selectStudyTargets(outlineNodes ?? []);

  const tasksByTarget = new Map<string, StudyTask[]>();
  for (const task of studyTasks ?? []) {
    if (!task.knowledge_point_id) continue;
    const list = tasksByTarget.get(task.knowledge_point_id) ?? [];
    list.push(task);
    tasksByTarget.set(task.knowledge_point_id, list);
  }

  const questionById = new Map((questions ?? []).map((question) => [question.id, question]));
  const questionCountByTarget = new Map<string, number>();
  for (const question of questions ?? []) {
    if (!question.knowledge_point_id) continue;
    questionCountByTarget.set(
      question.knowledge_point_id,
      (questionCountByTarget.get(question.knowledge_point_id) ?? 0) + 1
    );
  }

  const attemptsByQuestion = new Map<string, CourseAttempt[]>();
  const attemptsByTarget = new Map<string, CourseAttempt[]>();
  for (const attempt of attempts ?? []) {
    const questionAttempts = attemptsByQuestion.get(attempt.question_id) ?? [];
    questionAttempts.push(attempt);
    attemptsByQuestion.set(attempt.question_id, questionAttempts);

    const targetId = questionById.get(attempt.question_id)?.knowledge_point_id;
    if (!targetId) continue;

    const targetAttempts = attemptsByTarget.get(targetId) ?? [];
    targetAttempts.push(attempt);
    attemptsByTarget.set(targetId, targetAttempts);
  }

  const masteryRank: Record<MasteryLevel, number> = {
    weak: 0,
    reviewing: 1,
    untested: 2,
    mastered: 3,
  };

  const blueprintItems = studyTargets
    .map((target) => {
      const targetTasks = [...(tasksByTarget.get(target.id) ?? [])].sort((a, b) => a.priority - b.priority || a.order - b.order);
      const remainingTasks = targetTasks.filter((task) => task.status !== "done");
      const targetAttempts = attemptsByTarget.get(target.id) ?? [];
      const mastery = calculateMastery(targetAttempts);
      const questionCount = questionCountByTarget.get(target.id) ?? 0;
      const nextTask = remainingTasks[0] ?? targetTasks[0];

      return {
        id: target.id,
        title: target.title,
        content: target.content,
        nextAction: buildNextAction({
          title: target.title,
          nextTask,
          questionCount,
          masteryLevel: mastery.level,
          totalAttempts: mastery.total,
        }),
        taskCount: targetTasks.length,
        remainingTaskCount: remainingTasks.length,
        questionCount,
        masteryLevel: mastery.level,
        masteryRate: mastery.rate,
        totalAttempts: mastery.total,
        nextTaskType: nextTask?.task_type ?? null,
      };
    })
    .sort((a, b) => {
      const masteryDelta = masteryRank[a.masteryLevel] - masteryRank[b.masteryLevel];
      if (masteryDelta !== 0) return masteryDelta;
      if (a.remainingTaskCount !== b.remainingTaskCount) return b.remainingTaskCount - a.remainingTaskCount;
      if (a.questionCount !== b.questionCount) return b.questionCount - a.questionCount;
      return a.title.localeCompare(b.title);
    });

  const wrongNotebookItems = (questions ?? [])
    .map((question) => {
      const grouped = [...(attemptsByQuestion.get(question.id) ?? [])].sort(
        (a, b) => new Date(b.answered_at).getTime() - new Date(a.answered_at).getTime()
      );
      const wrongAttempts = grouped.filter((attempt) => !attempt.is_correct);
      if (wrongAttempts.length === 0) return null;

      const latestAttempt = grouped[0];
      const latestWrongAttempt = wrongAttempts[0];

      return {
        questionId: question.id,
        stem: question.stem,
        knowledgePointTitle: question.knowledge_point_id ? nodeTitleById.get(question.knowledge_point_id) ?? null : null,
        lastWrongAnswer: latestWrongAttempt.user_answer,
        correctAnswer: question.answer,
        explanation: question.explanation,
        wrongCount: wrongAttempts.length,
        lastWrongAt: latestWrongAttempt.answered_at,
        status: latestAttempt?.is_correct ? "fixed" as const : "needs_redo" as const,
      };
    })
    .filter((item): item is NonNullable<typeof item> => item !== null)
    .sort((a, b) => {
      if (a.status !== b.status) return a.status === "needs_redo" ? -1 : 1;
      return new Date(b.lastWrongAt).getTime() - new Date(a.lastWrongAt).getTime();
    });

  return (
    <div className="space-y-8">
      <Link href="/dashboard" className="ui-button-ghost w-fit !px-0">
        <ArrowLeft size={14} />
        Back to Dashboard
      </Link>

      <div className="ui-panel p-6 md:p-8">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <div className="ui-kicker mb-4">Course Space</div>
            <h1 className="text-4xl font-semibold tracking-tight">{course.title}</h1>
            {course.description && (
              <p className="ui-copy mt-3 max-w-3xl">{course.description}</p>
            )}
            <div className="flex flex-wrap gap-2 mt-5">
              {course.professor && <span className="ui-badge">{course.professor}</span>}
              {course.semester && <span className="ui-badge">{course.semester}</span>}
              <span className="ui-badge">{(outlineNodes ?? []).length} outline items</span>
              <span className="ui-badge">{(studyTasks ?? []).length} study tasks</span>
              <span className="ui-badge">{(questions ?? []).length} questions</span>
              <span className="ui-badge">{wrongNotebookItems.length} wrong notes</span>
              <span className="ui-badge">{notes.length} study notes</span>
            </div>
          </div>
          <div className="flex flex-wrap justify-end items-center gap-2">
            <a
              href={`/api/courses/${id}/export-anki`}
              download
              className="p-2 rounded-lg cursor-pointer"
              style={{ color: "var(--text-secondary)" }}
              title="Export to Anki"
            >
              <Download size={18} />
            </a>
            <RegenerateButton courseId={id} />
            <ShareButton courseId={id} />
            <ArchiveButton courseId={id} status={course.status} />
          </div>
        </div>
      </div>

      <CourseTabs courseId={id} />

      <LearningBlueprint courseId={id} items={blueprintItems} />

      <div className="grid gap-8 xl:grid-cols-[minmax(0,1.3fr)_minmax(320px,0.9fr)]">
        <section>
          <div className="mb-4">
            <div className="ui-kicker mb-3">Outline</div>
            <h2 className="text-2xl font-semibold">Course Map</h2>
            <p className="ui-copy mt-2">Use the map to see the structure, then use the study flow above to know what to do with it.</p>
          </div>
          <OutlineTree nodes={outlineNodes ?? []} courseId={id} />
        </section>

        <section>
          <StudyTrackerPanel
            courseId={id}
            activeMode="studying"
            title="Study Time"
            description="Reading the outline and working through tasks counts as study time. If the page sits untouched for a while, it shifts into idle."
            className="mb-6"
          />

          <div className="mb-6">
            <VoiceNotesPanel
              courseId={id}
              knowledgePoints={studyTargets.map((target) => ({ id: target.id, title: target.title }))}
              initialNotes={notes}
            />
          </div>

          <div className="mb-6">
            <ExamCountdown courseId={id} exams={exams ?? []} />
          </div>

          <StudyTaskList initialTasks={studyTasks ?? []} />
          <div className="mt-6">
            <WrongAnswerNotebook courseId={id} items={wrongNotebookItems} />
          </div>
        </section>
      </div>
    </div>
  );
}
