"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Archive, ArchiveRestore, Trash2 } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { useConfirm } from "@/components/ConfirmDialog";

export function ArchiveButton({ courseId, status }: { courseId: string; status: string }) {
  const router = useRouter();
  const { t } = useI18n();
  const { confirm, dialog } = useConfirm();
  const [error, setError] = useState<string | null>(null);

  async function toggleArchive() {
    setError(null);
    const newStatus = status === "active" ? "archived" : "active";
    const res = await fetch(`/api/courses/${courseId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
    });
    if (!res.ok) { setError(t("archive.archiveFailed")); return; }
    router.refresh();
  }

  async function deleteCourse() {
    if (!await confirm(t("archive.deleteConfirm"))) return;
    setError(null);
    const res = await fetch(`/api/courses/${courseId}`, { method: "DELETE" });
    if (!res.ok) { setError(t("archive.deleteFailed")); return; }
    router.push("/dashboard");
  }

  return (
    <div className="flex flex-col items-end gap-2">
      {dialog}
      <div className="flex flex-wrap justify-end gap-2">
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
      {error && (
        <p className="text-xs" style={{ color: "var(--danger)" }}>{error}</p>
      )}
    </div>
  );
}
