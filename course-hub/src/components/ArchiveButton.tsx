"use client";

import { useRouter } from "next/navigation";
import { Archive, ArchiveRestore, Trash2 } from "lucide-react";
import { useI18n } from "@/lib/i18n";

export function ArchiveButton({ courseId, status }: { courseId: string; status: string }) {
  const router = useRouter();
  const { t, locale } = useI18n();
  const isZh = locale === "zh";

  async function toggleArchive() {
    const newStatus = status === "active" ? "archived" : "active";
    await fetch(`/api/courses/${courseId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
    });
    router.refresh();
  }

  async function deleteCourse() {
    if (!confirm(isZh ? "删除这门课程及所有数据？" : "Delete this course and all its data?")) return;
    await fetch(`/api/courses/${courseId}`, { method: "DELETE" });
    router.push("/dashboard");
  }

  return (
    <div className="flex flex-wrap justify-end gap-2">
      <button
        onClick={toggleArchive}
        className="ui-button-secondary"
        title={status === "active" ? (isZh ? "归档" : "Archive") : (isZh ? "恢复" : "Restore")}
      >
        {status === "active" ? <Archive size={14} /> : <ArchiveRestore size={14} />}
        {status === "active" ? (isZh ? "归档" : "Archive") : (isZh ? "恢复" : "Restore")}
      </button>
      <button
        onClick={deleteCourse}
        className="ui-button-ghost"
        title={t("misc.delete")}
      >
        <Trash2 size={14} />
        {t("misc.delete")}
      </button>
    </div>
  );
}
