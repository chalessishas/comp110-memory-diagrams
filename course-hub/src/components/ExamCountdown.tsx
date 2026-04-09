"use client";

import { useState } from "react";
import { Calendar, Plus, Trash2, AlertTriangle } from "lucide-react";
import type { ExamDate } from "@/types";
import { useI18n } from "@/lib/i18n";

function daysUntil(dateStr: string): number {
  const exam = new Date(dateStr + "T23:59:59");
  const now = new Date();
  return Math.ceil((exam.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
}

function urgencyStyle(days: number): { color: string; bg: string } {
  if (days <= 3) return { color: "var(--danger)", bg: "var(--bg-muted)" };
  if (days <= 7) return { color: "var(--warning)", bg: "var(--bg-muted)" };
  return { color: "var(--text-secondary)", bg: "var(--bg-muted)" };
}

export function ExamCountdown({ courseId, exams: initialExams }: { courseId: string; exams: ExamDate[] }) {
  const { t } = useI18n();
  const [exams, setExams] = useState(initialExams);
  const [adding, setAdding] = useState(false);
  const [title, setTitle] = useState("");
  const [date, setDate] = useState("");

  async function handleAdd() {
    if (!title || !date) return;
    const res = await fetch(`/api/courses/${courseId}/exams`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, exam_date: date }),
    });
    if (res.ok) {
      const exam = await res.json();
      setExams((prev) => [...prev, exam].sort((a, b) => a.exam_date.localeCompare(b.exam_date)));
      setTitle("");
      setDate("");
      setAdding(false);
    }
  }

  async function handleDelete(examId: string) {
    await fetch(`/api/courses/${courseId}/exams`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ exam_id: examId }),
    });
    setExams((prev) => prev.filter((e) => e.id !== examId));
  }

  const upcoming = exams.filter((e) => daysUntil(e.exam_date) >= 0);

  return (
    <div className="ui-panel p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Calendar size={16} />
          <h3 className="text-sm font-medium">{t("exam.upcoming")}</h3>
        </div>
        <button
          onClick={() => setAdding(!adding)}
          className="p-1.5 cursor-pointer"
        >
          <Plus size={14} />
        </button>
      </div>

      {adding && (
        <div className="flex gap-2 mb-4">
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder={t("exam.namePlaceholder")}
            className="flex-1 px-3 py-2 text-xs outline-none transition-"
            onFocus={(e) => (e.currentTarget.style.boxShadow = "0 0 0 3px var(--accent-light)")}
            onBlur={(e) => (e.currentTarget.style.boxShadow = "none")}
          />
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="px-3 py-2 text-xs outline-none transition-"
            onFocus={(e) => (e.currentTarget.style.boxShadow = "0 0 0 3px var(--accent-light)")}
            onBlur={(e) => (e.currentTarget.style.boxShadow = "none")}
          />
          <button onClick={handleAdd} className="px-4 py-2 text-xs font-medium cursor-pointer">
            {t("exam.add")}
          </button>
        </div>
      )}

      {upcoming.length === 0 ? (
        <p className="text-xs">{t("exam.noUpcoming")}</p>
      ) : (
        <div className="space-y-2">
          {upcoming.map((exam) => {
            const days = daysUntil(exam.exam_date);
            const style = urgencyStyle(days);
            return (
              <div
                key={exam.id}
                className="flex items-center justify-between px-3.5 py-3 -[14px] group"
              >
                <div className="flex items-center gap-2.5">
                  {days <= 3 && <AlertTriangle size={12} />}
                  <span className="text-xs font-medium">{exam.title}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className="text-xs font-medium px-2 py-0.5"
                  >
                    {days === 0 ? t("exam.today") : days === 1 ? t("exam.tomorrow") : `${days} ${t("exam.days")}`}
                  </span>
                  <button onClick={() => handleDelete(exam.id)} className="opacity-0 group-hover:opacity-100 cursor-pointer">
                    <Trash2 size={11} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
