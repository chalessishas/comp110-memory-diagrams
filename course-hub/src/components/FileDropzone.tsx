"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, File, Loader2 } from "lucide-react";

interface FileDropzoneProps {
  onFileUploaded: (result: { storagePath: string; fileUrl: string; fileName: string; fileType: string }) => void;
  courseId?: string;
  accept?: Record<string, string[]>;
}

export function FileDropzone({ onFileUploaded, courseId, accept }: FileDropzoneProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);
    if (courseId) formData.append("courseId", courseId);

    const res = await fetch("/api/upload", { method: "POST", body: formData });
    const data = await res.json();

    if (!res.ok) {
      setError(data.error || "Upload failed");
      setUploading(false);
      return;
    }

    setUploading(false);
    onFileUploaded(data);
  }, [courseId, onFileUploaded]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxFiles: 1,
    maxSize: 30 * 1024 * 1024,
    accept,
  });

  return (
    <div className="ui-panel p-5 md:p-8">
      <div
        {...getRootProps()}
        className="rounded-[28px] border-2 border-dashed px-6 py-14 text-center cursor-pointer transition-colors"
        style={{
          borderColor: isDragActive ? "var(--text-primary)" : "var(--border-strong)",
          backgroundColor: isDragActive ? "rgba(16, 16, 16, 0.05)" : "rgba(247, 247, 244, 0.9)",
        }}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <div className="flex flex-col items-center gap-3">
            <Loader2 size={34} className="animate-spin" style={{ color: "var(--accent)" }} />
            <p className="text-sm font-medium">Uploading your file...</p>
            <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
              Hold tight while CourseHub prepares it for parsing.
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div
              className="flex h-16 w-16 items-center justify-center rounded-[22px]"
              style={{ backgroundColor: "white", border: "1px solid var(--border)" }}
            >
              {isDragActive ? (
                <File size={30} style={{ color: "var(--text-primary)" }} />
              ) : (
                <Upload size={30} style={{ color: "var(--text-secondary)" }} />
              )}
            </div>
            <div>
              <p className="text-base font-medium">
                {isDragActive ? "Drop the file here" : "Drag and drop a file, or click to browse"}
              </p>
              <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
                PDF, slides, images, or notes. CourseHub will sort the structure out for you.
              </p>
            </div>
            <div className="ui-kicker">Max 30 MB</div>
          </div>
        )}
      </div>
      {error && (
        <div
          className="mt-4 rounded-2xl px-4 py-3 text-sm"
          style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-muted)", color: "var(--danger)" }}
        >
          {error}
        </div>
      )}
    </div>
  );
}
