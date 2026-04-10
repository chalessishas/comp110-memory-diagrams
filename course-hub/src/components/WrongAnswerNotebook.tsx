"use client";

import Link from "next/link";
import { AlertCircle, ArrowRight, CheckCircle2, RotateCcw } from "lucide-react";
import { useI18n } from "@/lib/i18n";

interface WrongAnswerNotebookItem {
  questionId: string;
  stem: string;
  knowledgePointTitle: string | null;
  lastWrongAnswer: string;
  correctAnswer: string;
  explanation: string | null;
  wrongCount: number;
  lastWrongAt: string;
  status: "needs_redo" | "fixed";
}

function formatShortDate(value: string, locale: string) {
  return new Intl.DateTimeFormat(locale === "zh" ? "zh-CN" : "en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

export function WrongAnswerNotebook({
  courseId,
  items,
}: {
  courseId: string;
  items: WrongAnswerNotebookItem[];
}) {
  const { t, locale } = useI18n();
  return (
    <div id="wrong-notebook" className="ui-panel p-5 md:p-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <div className="ui-kicker mb-3">{t("wrongAnswer.kicker")}</div>
          <h3 className="text-2xl font-semibold tracking-wide">{t("wrongAnswer.headline")}</h3>
          <p className="ui-copy mt-2 max-w-2xl">
            {t("wrongAnswer.desc")}
          </p>
        </div>
        <Link href={`/course/${courseId}/practice`} className="ui-button-secondary">
          {t("wrongAnswer.redo")}
          <RotateCcw size={14} />
        </Link>
      </div>

      {items.length === 0 ? (
        <div className="ui-empty mt-6">
          <p className="text-base font-medium mb-2">{t("wrongAnswer.emptyTitle")}</p>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            {t("wrongAnswer.emptyDesc")}
          </p>
        </div>
      ) : (
        <div className="space-y-3 mt-6">
          {items.slice(0, 8).map((item) => (
            <div key={item.questionId} className="ui-panel px-5 py-4">
              <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <div className="flex flex-wrap gap-2">
                    <span
                      className="ui-badge"
                      style={{
                        backgroundColor: item.status === "needs_redo" ? "var(--danger-light, var(--bg-muted))" : "var(--success-light, var(--bg-muted))",
                      }}
                    >
                      {item.status === "needs_redo" ? (
                        <>
                          <AlertCircle size={12} style={{ color: "var(--danger)" }} />
                          {t("wrongAnswer.needsRedo")}
                        </>
                      ) : (
                        <>
                          <CheckCircle2 size={12} style={{ color: "var(--success)" }} />
                          {t("wrongAnswer.fixedOnce")}
                        </>
                      )}
                    </span>
                    {item.knowledgePointTitle && <span className="ui-badge">{item.knowledgePointTitle}</span>}
                    <span className="ui-badge">{t("wrongAnswer.misses", { count: item.wrongCount })}</span>
                  </div>
                  <p className="text-sm font-medium mt-3">{item.stem}</p>
                </div>
                <p className="text-xs shrink-0" style={{ color: "var(--text-muted)" }}>
                  {t("wrongAnswer.lastMiss")} {formatShortDate(item.lastWrongAt, locale)}
                </p>
              </div>

              <div className="grid gap-3 mt-4 lg:grid-cols-2">
                <div className="rounded-[20px] p-4" style={{ backgroundColor: "var(--bg-muted)" }}>
                  <p className="text-[11px] font-medium tracking-wide" style={{ color: "var(--text-muted)" }}>
                    {t("wrongAnswer.yourAnswer")}
                  </p>
                  <p className="text-sm mt-2 leading-relaxed">{item.lastWrongAnswer || t("wrongAnswer.noAnswer")}</p>
                </div>

                <div className="rounded-[20px] p-4" style={{ backgroundColor: "var(--bg-muted)" }}>
                  <p className="text-[11px] font-medium tracking-wide" style={{ color: "var(--text-muted)" }}>
                    {t("wrongAnswer.correctAnswer")}
                  </p>
                  <p className="text-sm mt-2 leading-relaxed">{item.correctAnswer}</p>
                </div>
              </div>

              {item.explanation && (
                <div className="rounded-[20px] p-4 mt-3" style={{ backgroundColor: "var(--bg-muted)" }}>
                  <p className="text-[11px] font-medium tracking-wide" style={{ color: "var(--text-muted)" }}>
                    {t("wrongAnswer.why")}
                  </p>
                  <p className="text-sm mt-2 leading-relaxed" style={{ color: "var(--text-secondary)" }}>
                    {item.explanation}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {items.length > 8 && (
        <div className="mt-5">
          <Link href={`/course/${courseId}/practice`} className="ui-button-ghost w-fit !px-0">
            See the rest in Practice
            <ArrowRight size={14} />
          </Link>
        </div>
      )}
    </div>
  );
}
