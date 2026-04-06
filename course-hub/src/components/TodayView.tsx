"use client";

import { AlertTriangle, RotateCcw, Calendar, BookOpen, Target, Check, Upload } from "lucide-react";
import Link from "next/link";
import { useI18n } from "@/lib/i18n";
import { StreakBadge } from "@/components/StreakBadge";

const typeIcons: Record<string, typeof AlertTriangle> = {
  urgent_study: AlertTriangle,
  exam_review: AlertTriangle,
  fsrs_review: RotateCcw,
  exam_prep: Calendar,
  new_content: BookOpen,
  weakness: Target,
};

const typeLabels: Record<string, { en: string; zh: string }> = {
  urgent_study: { en: "Urgent", zh: "紧急" },
  exam_review: { en: "Exam Review", zh: "考前排雷" },
  fsrs_review: { en: "Review", zh: "复习" },
  exam_prep: { en: "Exam Prep", zh: "考前准备" },
  new_content: { en: "New Content", zh: "新内容" },
  weakness: { en: "Weakness", zh: "弱点强化" },
};

interface TodayTask {
  id: string;
  type: string;
  priority: number;
  title: string;
  description: string;
  estimatedMinutes: number;
  count: number;
  color: string;
  courseId: string;
  courseTitle: string;
}

export function TodayView({ tasks, courseId }: { tasks: TodayTask[]; courseId: string }) {
  const { locale } = useI18n();
  const isZh = locale === "zh";

  // courseId available for future Start button routing
  void courseId;

  if (tasks.length === 0) {
    return (
      <div className="text-center py-16">
        <Check size={40} className="mx-auto mb-4" style={{ color: "var(--success)" }} />
        <h2 className="text-xl font-semibold mb-2">
          {isZh ? "今天状态很好！" : "You're all caught up!"}
        </h2>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          {isZh
            ? "没有紧急任务。可以提前预习，或者巩固复习。"
            : "No urgent tasks. Preview next week's content or review for fun."}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => {
        const Icon = typeIcons[task.type] ?? BookOpen;
        const label = typeLabels[task.type] ?? { en: task.type, zh: task.type };

        return (
          <div
            key={task.id}
            className="ui-panel p-5 flex items-start gap-4 group cursor-pointer transition-all overflow-hidden"
          >
            <div
              className="w-10 h-10 flex items-center justify-center shrink-0"
              style={{ backgroundColor: `${task.color}15`, color: task.color, borderRadius: "var(--radius-md)", border: `2px solid ${task.color}30` }}
            >
              <Icon size={18} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: task.color }}>
                  {isZh ? label.zh : label.en}
                </span>
                {task.count > 1 && (
                  <span className="ui-badge">{task.count}</span>
                )}
              </div>
              <p className="text-sm font-medium">{task.title}</p>
              <p className="text-xs mt-0.5" style={{ color: "var(--text-secondary)" }}>
                {task.description} · {task.estimatedMinutes} {isZh ? "分钟" : "min"}
              </p>
            </div>
            <button
              className="px-4 py-2 text-sm font-medium cursor-pointer shrink-0"
              style={{ backgroundColor: task.color, color: "white", borderRadius: "var(--radius-sm)" }}
            >
              {isZh ? "开始" : "Start"}
            </button>
          </div>
        );
      })}

      {/* Quick actions */}
      <div className="flex items-center gap-2 pt-4 mt-2" style={{ borderTop: "1px solid var(--border)" }}>
        <Link
          href={`/course/${courseId}/library`}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs cursor-pointer"
          style={{ borderRadius: "var(--radius-sm)", border: "1px solid var(--border)", color: "var(--text-secondary)" }}
        >
          <Upload size={12} />
          Upload material
        </Link>
        <div className="flex-1" />
        <StreakBadge />
      </div>
    </div>
  );
}
