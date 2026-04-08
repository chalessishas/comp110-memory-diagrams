"use client";

import { useEffect, useState, use } from "react";
import { CourseTabs } from "@/components/CourseTabs";
import { FileDropzone } from "@/components/FileDropzone";
import { FileText, Image, Presentation, Download, Trash2, Loader2, Upload as UploadIcon, File, Sparkles } from "lucide-react";
import type { Upload } from "@/types";
import { useI18n } from "@/lib/i18n";

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
  const { t } = useI18n();
  const [uploads, setUploads] = useState<UploadWithUrl[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [extracting, setExtracting] = useState<string | null>(null);

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

      <div className="flex items-center justify-between mb-8">
        <h2 className="text-lg font-semibold tracking-wide">{t("library.title")}</h2>
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="ui-button-secondary"
        >
          <UploadIcon size={14} />
          {t("library.uploadFile")}
        </button>
      </div>

      {showUpload && (
        <div className="mb-6">
          <FileDropzone onFileUploaded={handleFileUploaded} courseId={id} />
        </div>
      )}

      {uploads.length === 0 ? (
        <div className="ui-empty">
          <p className="mb-2" style={{ color: "var(--text-secondary)" }}>{t("library.noFiles")}</p>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            {t("library.noFilesDesc")}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {uploads.map((upload) => {
            const Icon = typeIcons[upload.file_type] ?? File;
            return (
              <div key={upload.id}>
                <div
                  className="flex items-center gap-3 px-4 py-3.5 rounded-[20px] group ui-panel"
                >
                  <Icon size={20} style={{ color: "var(--text-secondary)" }} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{upload.file_name}</p>
                    <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
                      {typeLabels[upload.upload_type] ?? "File"} · {formatDate(upload.created_at)}
                    </p>
                  </div>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    {(upload.file_type === "pdf" || upload.file_type === "image") && !upload.parsed_content && (
                      <button
                        onClick={async () => {
                          const pathMatch = upload.file_url.match(/course-files\/(.+)$/);
                          if (!pathMatch) return;
                          setExtracting(upload.id);
                          const res = await fetch(`/api/courses/${id}/extract`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ storagePath: pathMatch[1] }),
                          });
                          if (res.ok) {
                            const data = await res.json();
                            setUploads((prev) => prev.map((u) => u.id === upload.id ? { ...u, parsed_content: data } : u));
                          }
                          setExtracting(null);
                        }}
                        disabled={extracting === upload.id}
                        className="p-2 cursor-pointer rounded-lg hover:opacity-80"
                        title="Extract key content with AI"
                      >
                        {extracting === upload.id ? (
                          <Loader2 size={15} className="animate-spin" style={{ color: "var(--text-secondary)" }} />
                        ) : (
                          <Sparkles size={15} style={{ color: "var(--accent)" }} />
                        )}
                      </button>
                    )}
                    {upload.download_url && (
                      <a
                        href={upload.download_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 cursor-pointer rounded-lg hover:opacity-80"
                        title="Download"
                      >
                        <Download size={15} style={{ color: "var(--text-secondary)" }} />
                      </a>
                    )}
                    <button
                      onClick={() => handleDelete(upload.id)}
                      disabled={deleting === upload.id}
                      className="p-2 cursor-pointer rounded-lg hover:opacity-80"
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
                {upload.parsed_content != null && (
                  <div className="mt-2 ml-9 space-y-2">
                    {(upload.parsed_content as any).sections?.map((section: any, i: number) => (
                      <div key={i} className="p-3 rounded-xl text-xs" style={{ backgroundColor: "var(--bg-muted)" }}>
                        <p className="font-medium">{section.title}</p>
                        <p className="mt-1" style={{ color: "var(--text-secondary)" }}>{section.summary}</p>
                        {section.key_concepts?.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {section.key_concepts.map((c: string, j: number) => (
                              <span key={j} className="ui-badge">
                                {c}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
