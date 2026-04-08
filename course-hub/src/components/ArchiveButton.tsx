"use client";

import { useRouter } from "next/navigation";
import { Archive, ArchiveRestore, Trash2 } from "lucide-react";
import { useI18n } from "@/lib/i18n";

export function ArchiveButton({ courseId, status }: { courseId: string; status: string }) {
  const router = useRouter();
  const { t } = useI18n();

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
    if (!confirm(t("courses.confirmDelete"))) return;
    await fetch(`/api/courses/${courseId}`, { method: "DELETE" });
    router.push("/dashboard");
  }

  return (
    <div className="flex flex-wrap justify-end gap-2">
      <button
        onClick={toggleArchive}
        className="ui-button-secondary !px-4 !py-3 !text-sm"
        title={status === "active" ? t("courses.archive") : t("courses.restore")}
      >
        {status === "active" ? <Archive size={16} /> : <ArchiveRestore size={16} />}
        {status === "active" ? t("courses.archive") : t("courses.restore")}
      </button>
      <button
        onClick={deleteCourse}
        className="ui-button-secondary !px-4 !py-3 !text-sm"
        style={{ color: "var(--text-secondary)" }}
        title={t("courses.delete")}
      >
        <Trash2 size={16} />
        {t("courses.delete")}
      </button>
    </div>
  );
}
