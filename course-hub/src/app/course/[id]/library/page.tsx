"use client";

import { useEffect, useState, use } from "react";
import { CourseTabs } from "@/components/CourseTabs";
import { FileDropzone } from "@/components/FileDropzone";
import { FileText, Image, Presentation, Download, Trash2, Loader2, Upload as UploadIcon, File } from "lucide-react";
import type { Upload } from "@/types";

type UploadWithUrl = Upload & { download_url: string | null };

const typeIcons: Record<string, typeof FileText> = {
  pdf: FileText,
  ppt: Presentation,
  image: Image,
  text: FileText,
  other: File,
};

const typeLabels: Record<string, string> = {
  syllabus: "Syllabus",
  exam: "Exam",
  practice: "Practice",
  notes: "Notes",
  other: "Other",
};

function formatDate(dateStr: string) {
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(dateStr));
}

export default function LibraryPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [uploads, setUploads] = useState<UploadWithUrl[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);

  useEffect(() => {
    fetch(`/api/courses/${id}/uploads`)
      .then((r) => r.json())
      .then((data) => { setUploads(data); setLoading(false); });
  }, [id]);

  async function handleFileUploaded() {
    // Refresh list after upload
    const res = await fetch(`/api/courses/${id}/uploads`);
    const data = await res.json();
    setUploads(data);
    setShowUpload(false);
  }

  async function handleDelete(uploadId: string) {
    if (!confirm("Delete this file?")) return;
    setDeleting(uploadId);
    await fetch(`/api/courses/${id}/uploads`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ upload_id: uploadId }),
    });
    setUploads((prev) => prev.filter((u) => u.id !== uploadId));
    setDeleting(null);
  }

  if (loading) return (
    <div>
      <CourseTabs courseId={id} />
      <Loader2 className="animate-spin mx-auto mt-16" style={{ color: "var(--text-secondary)" }} />
    </div>
  );

  return (
    <div>
      <CourseTabs courseId={id} />

      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-medium">Course Library</h2>
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-sm cursor-pointer"
          style={{ border: "1px solid var(--border)", color: "var(--text-secondary)" }}
        >
          <UploadIcon size={14} />
          Upload File
        </button>
      </div>

      {showUpload && (
        <div className="mb-6">
          <FileDropzone onFileUploaded={handleFileUploaded} courseId={id} />
        </div>
      )}

      {uploads.length === 0 ? (
        <div className="text-center py-16">
          <p className="mb-2" style={{ color: "var(--text-secondary)" }}>No files yet</p>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            Upload textbooks, slides, past exams — all stored in the cloud
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {uploads.map((upload) => {
            const Icon = typeIcons[upload.file_type] ?? File;
            return (
              <div
                key={upload.id}
                className="flex items-center gap-3 px-4 py-3 rounded-2xl group"
                style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}
              >
                <Icon size={20} style={{ color: "var(--text-secondary)" }} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{upload.file_name}</p>
                  <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
                    {typeLabels[upload.upload_type] ?? "File"} · {formatDate(upload.created_at)}
                  </p>
                </div>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {upload.download_url && (
                    <a
                      href={upload.download_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-2 cursor-pointer rounded-lg hover:bg-black/5"
                      title="Download"
                    >
                      <Download size={15} style={{ color: "var(--text-secondary)" }} />
                    </a>
                  )}
                  <button
                    onClick={() => handleDelete(upload.id)}
                    disabled={deleting === upload.id}
                    className="p-2 cursor-pointer rounded-lg hover:bg-black/5"
                    title="Delete"
                  >
                    {deleting === upload.id ? (
                      <Loader2 size={15} className="animate-spin" style={{ color: "var(--text-secondary)" }} />
                    ) : (
                      <Trash2 size={15} style={{ color: "var(--danger)" }} />
                    )}
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
