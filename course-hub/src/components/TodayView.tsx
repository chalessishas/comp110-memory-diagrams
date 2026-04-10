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
  actionUrl: string;
}

export function TodayView({ tasks, courseId }: { tasks: TodayTask[]; courseId: string }) {
  const { locale } = useI18n();
  const isZh = locale === "zh";

  // courseId available for future Start button routing
  void courseId;

  if (tasks.length === 0) {
    return (
      <div className="text-center py-20">
        <div
          className="mx-auto mb-5 w-14 h-14 flex items-center justify-center rounded-full"
          style={{ backgroundColor: "var(--bg-muted)" }}
        >
          <Check size={28} strokeWidth={1.8} style={{ color: "var(--success)" }} />
        </div>
        <h2
          className="text-xl font-semibold mb-2"
          style={{ color: "var(--text-primary)" }}
        >
          {isZh ? "今天状态很好！" : "You're all caught up!"}
        </h2>
        <p className="text-sm" style={{ color: "var(--text-muted)" }}>
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
          <Link
            key={task.id}
            href={task.actionUrl}
            className="ui-panel p-5 rounded-[20px] flex items-start gap-4 group cursor-pointer transition-all overflow-hidden hover:-translate-y-0.5"
          >
            {/* Priority dot — left indicator */}
            <div className="flex flex-col items-center pt-1.5 shrink-0">
              <div
                className="w-2.5 h-2.5 rounded-full"
                style={{ backgroundColor: task.color }}
              />
            </div>

            {/* Icon */}
            <div
              className="w-9 h-9 flex items-center justify-center shrink-0 rounded-xl"
              style={{ backgroundColor: "var(--bg-muted)", color: task.color }}
            >
              <Icon size={16} strokeWidth={1.8} />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-0.5">
                <span
                  className="text-xs font-medium"
                  style={{ color: task.color }}
                >
                  {isZh ? label.zh : label.en}
                </span>
                {task.count > 1 && (
                  <span className="ui-badge">{task.count}</span>
                )}
              </div>
              <p
                className="text-sm font-medium leading-snug"
                style={{ color: "var(--text-primary)" }}
              >
                {task.title}
              </p>
              <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                {task.description} · {task.estimatedMinutes} {isZh ? "分钟" : "min"}
              </p>
            </div>

            {/* Start indicator */}
            <span
              className="px-4 py-2 text-sm font-medium shrink-0 rounded-xl"
              style={{ backgroundColor: task.color, color: "white" }}
            >
              {isZh ? "开始" : "Start"}
            </span>
          </Link>
        );
      })}

      {/* Quick actions */}
      <div className="flex items-center gap-3 pt-5 mt-3">
        <Link
          href={`/course/${courseId}/library`}
          className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium cursor-pointer rounded-xl transition-all"
          style={{ backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)" }}
        >
          <Upload size={12} strokeWidth={1.8} />
          {isZh ? "上传资料" : "Upload material"}
        </Link>
        <div className="flex-1" />
        <StreakBadge />
      </div>
    </div>
  );
}
