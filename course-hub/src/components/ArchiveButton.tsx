"use client";

import { useRouter } from "next/navigation";
import { Archive, ArchiveRestore, Trash2 } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { useConfirm } from "@/components/ConfirmDialog";

export function ArchiveButton({ courseId, status }: { courseId: string; status: string }) {
  const router = useRouter();
  const { t } = useI18n();
  const { confirm, dialog } = useConfirm();

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
    if (!await confirm(t("archive.deleteConfirm"))) return;
    await fetch(`/api/courses/${courseId}`, { method: "DELETE" });
    router.push("/dashboard");
  }

  return (
    <div className="flex flex-wrap justify-end gap-2">
      {dialog}
      <button
        onClick={toggleArchive}
        className="ui-button-secondary"
        title={status === "active" ? t("archive.archive") : t("archive.restore")}
      >
        {status === "active" ? <Archive size={14} /> : <ArchiveRestore size={14} />}
        {status === "active" ? t("archive.archive") : t("archive.restore")}
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
