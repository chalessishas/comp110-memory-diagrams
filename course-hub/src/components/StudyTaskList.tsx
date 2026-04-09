"use client";

import { useState } from "react";
import { Check, Circle, BookOpen, PenLine, RotateCcw, Loader2 } from "lucide-react";
import type { StudyTask } from "@/types";
import { useI18n } from "@/lib/i18n";

const typeIcons = {
  read: BookOpen,
  practice: PenLine,
  review: RotateCcw,
};

const priorityColors = {
  1: "var(--danger)",
  2: "var(--warning)",
  3: "var(--text-secondary)",
};

export function StudyTaskList({ initialTasks }: { initialTasks: StudyTask[] }) {
  const { t } = useI18n();
  const [tasks, setTasks] = useState(initialTasks);
  const [toggling, setToggling] = useState<string | null>(null);

  const typeLabels: Record<string, string> = {
    read: t("studyTask.typeRead"),
    practice: t("studyTask.typePractice"),
    review: t("studyTask.typeReview"),
  };

  const priorityLabels: Record<number, string> = {
    1: t("studyTask.mustKnow"),
    2: t("studyTask.shouldKnow"),
    3: t("studyTask.niceToKnow"),
  };

  async function toggleTask(taskId: string, currentStatus: string) {
    setToggling(taskId);
    const newStatus = currentStatus === "todo" ? "done" : "todo";

    await fetch(`/api/study-tasks/${taskId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
    });

    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, status: newStatus as "todo" | "done" } : t))
    );
    setToggling(null);
  }

  if (tasks.length === 0) {
    return (
      <div className="ui-panel p-5 md:p-6">
        <div className="ui-kicker mb-3">Study Tasks</div>
        <h3 className="text-2xl font-semibold tracking-wide">Keep the work concrete.</h3>
        <p className="ui-copy mt-2">
          A focused checklist generated from the course outline.
        </p>
        <div className="ui-empty mt-6">
          <p className="text-sm">
            No study tasks yet. Generate the course content first and they will show up here.
          </p>
        </div>
      </div>
    );
  }

  const todoTasks = tasks.filter((t) => t.status === "todo");
  const doneTasks = tasks.filter((t) => t.status === "done");
  const progress = tasks.length > 0 ? Math.round((doneTasks.length / tasks.length) * 100) : 0;

  const byPriority = [1, 2, 3].map((p) => ({
    priority: p as 1 | 2 | 3,
    tasks: todoTasks.filter((t) => t.priority === p),
  })).filter((g) => g.tasks.length > 0);

  return (
    <div className="ui-panel p-5 md:p-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between mb-6">
        <div>
          <div className="ui-kicker mb-3">Study Tasks</div>
          <h3 className="text-2xl font-semibold tracking-wide">Keep the work concrete.</h3>
          <p className="ui-copy mt-2">
            A focused checklist generated from the course outline.
          </p>
        </div>
        <div className="min-w-[190px]">
          <div className="flex items-center justify-between text-xs mb-2">
            <span>Progress</span>
            <span>{doneTasks.length}/{tasks.length}</span>
          </div>
          <div className="ui-progress-track">
            <div className="ui-progress-bar" />
          </div>
        </div>
      </div>

      {byPriority.map((group) => (
        <div key={group.priority} className="mb-5 last:mb-0">
          <p className="text-[11px] font-medium tracking-wide mb-3">
            {priorityLabels[group.priority]}
          </p>
          <div className="space-y-2">
            {group.tasks.map((task) => {
              const Icon = typeIcons[task.task_type];
              return (
                <div
                  key={task.id}
                  className="flex items-start gap-3 -[20px] px-5 py-4 group"
                >
                  <button
                    onClick={() => toggleTask(task.id, task.status)}
                    disabled={toggling === task.id}
                    className="mt-0.5 shrink-0 cursor-pointer"
                  >
                    {toggling === task.id ? (
                      <Loader2 size={16} className="animate-spin" />
                    ) : (
                      <div className="flex items-center gap-0">
                        <span
                          className="inline-block w-[6px] h-[6px] mr-2"
                        />
                        <Circle size={18} className="" />
                      </div>
                    )}
                  </button>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{task.title}</p>
                    <p className="text-sm mt-1 leading-relaxed">{task.description}</p>
                  </div>
                  <span className="ui-badge shrink-0">
                    <Icon size={12} />
                    {typeLabels[task.task_type]}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      ))}

      {doneTasks.length > 0 && (
        <details className="mt-6">
          <summary className="text-[11px] cursor-pointer font-medium tracking-wide">
            Completed ({doneTasks.length})
          </summary>
          <div className="space-y-2 mt-3 opacity-60">
            {doneTasks.map((task) => (
              <div
                key={task.id}
                className="flex items-center gap-3 -[20px] px-5 py-3"
              >
                <button onClick={() => toggleTask(task.id, task.status)} className="shrink-0 cursor-pointer">
                  <Check size={16} />
                </button>
                <p className="text-sm line-through">{task.title}</p>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  );
}
