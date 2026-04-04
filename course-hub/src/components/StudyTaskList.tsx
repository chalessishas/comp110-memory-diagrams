"use client";

import { useState } from "react";
import { Check, Circle, BookOpen, PenLine, RotateCcw, Loader2 } from "lucide-react";
import type { StudyTask } from "@/types";

const typeIcons = {
  read: BookOpen,
  practice: PenLine,
  review: RotateCcw,
};

const typeLabels = {
  read: "Read",
  practice: "Practice",
  review: "Review",
};

const priorityLabels = {
  1: "Must Know",
  2: "Should Know",
  3: "Nice to Know",
};

const priorityColors = {
  1: "var(--danger)",
  2: "var(--warning)",
  3: "var(--text-secondary)",
};

export function StudyTaskList({ initialTasks }: { initialTasks: StudyTask[] }) {
  const [tasks, setTasks] = useState(initialTasks);
  const [toggling, setToggling] = useState<string | null>(null);

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
        <h3 className="text-2xl font-semibold">Keep the work concrete.</h3>
        <p className="ui-copy mt-2">
          A focused checklist generated from the course outline.
        </p>
        <div className="ui-empty mt-6">
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            No study tasks yet. Generate the course content first and they will show up here.
          </p>
        </div>
      </div>
    );
  }

  const todoTasks = tasks.filter((t) => t.status === "todo");
  const doneTasks = tasks.filter((t) => t.status === "done");
  const progress = tasks.length > 0 ? Math.round((doneTasks.length / tasks.length) * 100) : 0;

  // Group by priority
  const byPriority = [1, 2, 3].map((p) => ({
    priority: p as 1 | 2 | 3,
    tasks: todoTasks.filter((t) => t.priority === p),
  })).filter((g) => g.tasks.length > 0);

  return (
    <div className="ui-panel p-5 md:p-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between mb-6">
        <div>
          <div className="ui-kicker mb-3">Study Tasks</div>
          <h3 className="text-2xl font-semibold">Keep the work concrete.</h3>
          <p className="ui-copy mt-2">
            A focused checklist generated from the course outline.
          </p>
        </div>
        <div className="min-w-[190px]">
          <div className="flex items-center justify-between text-xs mb-2" style={{ color: "var(--text-secondary)" }}>
            <span>Progress</span>
            <span>{doneTasks.length}/{tasks.length}</span>
          </div>
          <div className="ui-progress-track">
            <div className="ui-progress-bar transition-all" style={{ width: `${progress}%` }} />
          </div>
        </div>
      </div>

      {byPriority.map((group) => (
        <div key={group.priority} className="mb-5 last:mb-0">
          <p className="text-[11px] font-semibold uppercase tracking-[0.24em] mb-3" style={{ color: priorityColors[group.priority] }}>
            {priorityLabels[group.priority]}
          </p>
          <div className="space-y-2">
            {group.tasks.map((task) => {
              const Icon = typeIcons[task.task_type];
              return (
                <div
                  key={task.id}
                  className="flex items-start gap-3 rounded-[24px] px-4 py-4 transition-colors group"
                  style={{ backgroundColor: "rgba(247, 247, 244, 0.92)", border: "1px solid var(--border)" }}
                >
                  <button
                    onClick={() => toggleTask(task.id, task.status)}
                    disabled={toggling === task.id}
                    className="mt-0.5 shrink-0 cursor-pointer rounded-full"
                  >
                    {toggling === task.id ? (
                      <Loader2 size={16} className="animate-spin" style={{ color: "var(--text-secondary)" }} />
                    ) : (
                      <Circle size={18} style={{ color: "var(--border-strong)" }} />
                    )}
                  </button>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{task.title}</p>
                    <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>{task.description}</p>
                  </div>
                  <span className="flex items-center gap-1 text-xs shrink-0 px-3 py-1.5 rounded-full"
                    style={{ backgroundColor: "white", color: "var(--text-secondary)", border: "1px solid var(--border)" }}>
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
          <summary className="text-xs cursor-pointer font-semibold uppercase tracking-[0.22em]" style={{ color: "var(--text-secondary)" }}>
            Completed ({doneTasks.length})
          </summary>
          <div className="space-y-2 mt-3 opacity-65">
            {doneTasks.map((task) => (
              <div
                key={task.id}
                className="flex items-center gap-3 rounded-[22px] px-4 py-3"
                style={{ backgroundColor: "white", border: "1px solid var(--border)" }}
              >
                <button onClick={() => toggleTask(task.id, task.status)} className="shrink-0 cursor-pointer rounded-full">
                  <Check size={16} style={{ color: "var(--success)" }} />
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
