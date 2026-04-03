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

  if (tasks.length === 0) return null;

  const todoTasks = tasks.filter((t) => t.status === "todo");
  const doneTasks = tasks.filter((t) => t.status === "done");
  const progress = tasks.length > 0 ? Math.round((doneTasks.length / tasks.length) * 100) : 0;

  // Group by priority
  const byPriority = [1, 2, 3].map((p) => ({
    priority: p as 1 | 2 | 3,
    tasks: todoTasks.filter((t) => t.priority === p),
  })).filter((g) => g.tasks.length > 0);

  return (
    <div className="mt-8">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium">Study Tasks</h3>
        <div className="flex items-center gap-2">
          <div className="w-32 h-2 rounded-full" style={{ backgroundColor: "var(--border)" }}>
            <div
              className="h-2 rounded-full transition-all"
              style={{ width: `${progress}%`, backgroundColor: "var(--success)" }}
            />
          </div>
          <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
            {doneTasks.length}/{tasks.length}
          </span>
        </div>
      </div>

      {byPriority.map((group) => (
        <div key={group.priority} className="mb-4">
          <p className="text-xs font-medium uppercase tracking-wider mb-2" style={{ color: priorityColors[group.priority] }}>
            {priorityLabels[group.priority]}
          </p>
          <div className="space-y-1">
            {group.tasks.map((task) => {
              const Icon = typeIcons[task.task_type];
              return (
                <div
                  key={task.id}
                  className="flex items-start gap-3 px-3 py-2.5 rounded-lg transition-colors group"
                  style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}
                >
                  <button
                    onClick={() => toggleTask(task.id, task.status)}
                    disabled={toggling === task.id}
                    className="mt-0.5 shrink-0 cursor-pointer"
                  >
                    {toggling === task.id ? (
                      <Loader2 size={16} className="animate-spin" style={{ color: "var(--text-secondary)" }} />
                    ) : (
                      <Circle size={16} style={{ color: "var(--border)" }} />
                    )}
                  </button>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{task.title}</p>
                    <p className="text-xs mt-0.5" style={{ color: "var(--text-secondary)" }}>{task.description}</p>
                  </div>
                  <span className="flex items-center gap-1 text-xs shrink-0 px-2 py-0.5 rounded"
                    style={{ backgroundColor: "var(--bg-primary)", color: "var(--text-secondary)" }}>
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
        <details className="mt-4">
          <summary className="text-xs cursor-pointer" style={{ color: "var(--text-secondary)" }}>
            Completed ({doneTasks.length})
          </summary>
          <div className="space-y-1 mt-2 opacity-50">
            {doneTasks.map((task) => (
              <div
                key={task.id}
                className="flex items-center gap-3 px-3 py-2 rounded-lg"
                style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}
              >
                <button onClick={() => toggleTask(task.id, task.status)} className="shrink-0 cursor-pointer">
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
