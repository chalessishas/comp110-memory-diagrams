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
    <div className="flex gap-1">
      <button onClick={toggleArchive} className="p-2 rounded-lg cursor-pointer" style={{ color: "var(--text-secondary)" }}
        title={status === "active" ? "Archive" : "Restore"}>
        {status === "active" ? <Archive size={18} /> : <ArchiveRestore size={18} />}
      </button>
      <button onClick={deleteCourse} className="p-2 rounded-lg cursor-pointer" style={{ color: "var(--danger)" }} title="Delete">
        <Trash2 size={18} />
      </button>
    </div>
  );
}
