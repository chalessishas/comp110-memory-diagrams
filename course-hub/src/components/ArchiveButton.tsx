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
        className="ui-button-secondary !px-4 !py-3 !text-sm"
        title={status === "active" ? "Archive" : "Restore"}
      >
        {status === "active" ? <Archive size={16} /> : <ArchiveRestore size={16} />}
        {status === "active" ? "Archive" : "Restore"}
      </button>
      <button
        onClick={deleteCourse}
        className="ui-button-secondary !px-4 !py-3 !text-sm"
        style={{ color: "var(--text-secondary)" }}
        title="Delete"
      >
        <Trash2 size={16} />
        Delete
      </button>
    </div>
  );
}
