"use client";

import Link from "next/link";
import { ArrowRight, BookOpenText, PenLine, RotateCcw } from "lucide-react";
import { masteryColors, masteryLabels } from "@/lib/mastery";
import { useI18n } from "@/lib/i18n";
import type { MasteryLevel, TaskType } from "@/types";

interface LearningBlueprintItem {
  id: string;
  title: string;
  content: string | null;
  nextAction: string;
  taskCount: number;
  remainingTaskCount: number;
  questionCount: number;
  masteryLevel: MasteryLevel;
  masteryRate: number;
  totalAttempts: number;
  nextTaskType: TaskType | null;
}

const taskIcons = {
  read: BookOpenText,
  practice: PenLine,
  review: RotateCcw,
};

function rateLabel(rate: number, totalAttempts: number, t: (key: string) => string) {
  if (totalAttempts === 0) return t("blueprint.noAttempts");
  return `${Math.round(rate * 100)}% ${t("blueprint.correct")}`;
}

export function LearningBlueprint({
  courseId,
  items,
}: {
  courseId: string;
  items: LearningBlueprintItem[];
}) {
  const { t } = useI18n();

  if (items.length === 0) {
    return (
      <div className="ui-panel p-6 md:p-8">
        <div className="ui-kicker mb-3">{t("blueprint.kicker")}</div>
        <h2 className="text-2xl font-semibold">{t("blueprint.emptyTitle")}</h2>
        <p className="ui-copy mt-2 max-w-2xl">
          {t("blueprint.emptyDesc")}
        </p>
      </div>
    );
  }

  const visibleItems = items.slice(0, 6);

  return (
    <div className="ui-panel p-6 md:p-8">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="ui-kicker mb-3">{t("blueprint.kicker")}</div>
          <h2 className="text-2xl font-semibold">{t("blueprint.title")}</h2>
          <p className="ui-copy mt-2 max-w-3xl">
            {t("blueprint.desc")}
          </p>
        </div>
        <Link href={`/course/${courseId}/practice`} className="ui-button-secondary">
          {t("blueprint.openPractice")}
          <ArrowRight size={14} />
        </Link>
      </div>

      <div className="grid gap-4 mt-6 xl:grid-cols-2">
        {visibleItems.map((item, index) => {
          const TaskIcon = item.nextTaskType ? taskIcons[item.nextTaskType] : ArrowRight;

          return (
            <div
              key={item.id}
              className="rounded-md p-5"
              style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-surface)" }}
            >
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.22em]" style={{ color: "var(--text-secondary)" }}>
                    {index === 0 ? t("blueprint.startHere") : `${t("blueprint.step")} ${index + 1}`}
                  </p>
                  <h3 className="text-lg font-semibold mt-2">{item.title}</h3>
                  {item.content && (
                    <p className="text-sm mt-2" style={{ color: "var(--text-secondary)" }}>
                      {item.content}
                    </p>
                  )}
                </div>
                <span
                  className="shrink-0 rounded px-3 py-1.5 text-xs font-medium"
                  style={{
                    backgroundColor: "white",
                    color: item.masteryLevel === "mastered" ? "white" : "var(--text-primary)",
                    border: `1px solid ${item.masteryLevel === "mastered" ? masteryColors[item.masteryLevel] : "var(--border)"}`,
                    ...(item.masteryLevel === "mastered" ? { backgroundColor: masteryColors[item.masteryLevel] } : {}),
                  }}
                >
                  {masteryLabels[item.masteryLevel]}
                </span>
              </div>

              <div className="flex flex-wrap gap-2 mt-4">
                <span className="ui-badge">{item.remainingTaskCount}/{item.taskCount} {t("blueprint.tasksLeft")}</span>
                <span className="ui-badge">{item.questionCount} {t("blueprint.questions")}</span>
                <span className="ui-badge">{rateLabel(item.masteryRate, item.totalAttempts, t)}</span>
              </div>

              <div
                className="rounded-md px-4 py-4 mt-4"
                style={{ border: "1px solid var(--border)", backgroundColor: "white" }}
              >
                <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em]" style={{ color: "var(--text-secondary)" }}>
                  <TaskIcon size={14} />
                  {item.nextTaskType ? t(`studyTask.type${item.nextTaskType[0].toUpperCase()}${item.nextTaskType.slice(1)}`) : t("blueprint.nextMove")}
                </div>
                <p className="text-sm mt-2">{item.nextAction}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
