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

const typeLabelKeys: Record<string, string> = {
  urgent_study: "today.urgent",
  exam_review: "today.examReview",
  fsrs_review: "today.review",
  exam_prep: "today.examPrep",
  new_content: "today.newContent",
  weakness: "today.weakness",
};

interface TodayTask {
  id: string;
  type: string;
  priority: number;
  title: string;
  titleKey?: string;
  titleVars?: Record<string, string | number>;
  description: string;
  descKey?: string;
  descVars?: Record<string, string | number>;
  estimatedMinutes: number;
  count: number;
  color: string;
  courseId: string;
  courseTitle: string;
  actionUrl: string;
}

export function TodayView({ tasks, courseId }: { tasks: TodayTask[]; courseId: string }) {
  const { t } = useI18n();

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
          {t("today.allCaughtUp")}
        </h2>
        <p className="text-sm" style={{ color: "var(--text-muted)" }}>
          {t("today.allCaughtUpDesc")}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => {
        const Icon = typeIcons[task.type] ?? BookOpen;

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
                  {t(typeLabelKeys[task.type] ?? task.type)}
                </span>
                {task.count > 1 && (
                  <span className="ui-badge">{task.count}</span>
                )}
              </div>
              <p
                className="text-sm font-medium leading-snug"
                style={{ color: "var(--text-primary)" }}
              >
                {task.titleKey ? t(task.titleKey, task.titleVars) : task.title}
              </p>
              <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                {task.descKey ? t(task.descKey, task.descVars) : task.description} · {task.estimatedMinutes} {t("today.estimatedTime")}
              </p>
            </div>

            {/* Start indicator */}
            <span
              className="px-4 py-2 text-sm font-medium shrink-0 rounded-xl"
              style={{ backgroundColor: task.color, color: "white" }}
            >
              {t("today.startButton")}
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
          {t("learn.uploadMaterial")}
        </Link>
        <div className="flex-1" />
        <StreakBadge />
      </div>
    </div>
  );
}
