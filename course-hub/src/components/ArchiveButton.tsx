"use client";

import { useRouter } from "next/navigation";
import { Archive, ArchiveRestore, Trash2 } from "lucide-react";

export function ArchiveButton({ courseId, status }: { courseId: string; status: string }) {
  const router = useRouter();

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
    if (!confirm("Delete this course and all its data?")) return;
    await fetch(`/api/courses/${courseId}`, { method: "DELETE" });
    router.push("/dashboard");
  }

  return (
    <div className="flex flex-wrap justify-end gap-2">
      <button
        onClick={toggleArchive}
        className="ui-button-secondary"
        title={status === "active" ? "Archive" : "Restore"}
      >
        {status === "active" ? <Archive size={14} /> : <ArchiveRestore size={14} />}
        {status === "active" ? "Archive" : "Restore"}
      </button>
      <button
        onClick={deleteCourse}
        className="ui-button-ghost"
        title="Delete"
      >
        <Trash2 size={14} />
        Delete
      </button>
    </div>
  );
}
