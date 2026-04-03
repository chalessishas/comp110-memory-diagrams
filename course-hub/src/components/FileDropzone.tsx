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
    <div
      {...getRootProps()}
      className="border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors"
      style={{
        borderColor: isDragActive ? "var(--accent)" : "var(--border)",
        backgroundColor: isDragActive ? "rgba(196, 169, 125, 0.05)" : "transparent",
      }}
    >
      <input {...getInputProps()} />
      {uploading ? (
        <div className="flex flex-col items-center gap-2">
          <Loader2 size={32} className="animate-spin" style={{ color: "var(--accent)" }} />
          <p style={{ color: "var(--text-secondary)" }}>Uploading...</p>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-2">
          {isDragActive ? (
            <File size={32} style={{ color: "var(--accent)" }} />
          ) : (
            <Upload size={32} style={{ color: "var(--text-secondary)" }} />
          )}
          <p style={{ color: "var(--text-secondary)" }}>
            {isDragActive ? "Drop file here" : "Drag & drop any file, or click to browse"}
          </p>
          <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
            PDF, PPT, images, text — AI will figure out the rest
          </p>
        </div>
      )}
      {error && <p className="text-sm mt-2" style={{ color: "var(--danger)" }}>{error}</p>}
    </div>
  );
}
