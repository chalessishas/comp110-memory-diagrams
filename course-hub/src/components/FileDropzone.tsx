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
        className="-[20px] px-6 py-14 text-center cursor-pointer"
      >
        <input {...getInputProps()} />
        {uploading ? (
          <div className="flex flex-col items-center gap-3">
            <Loader2 size={34} className="animate-spin" />
            <p className="text-sm font-medium">Uploading your file...</p>
            <p className="text-xs">
              Hold tight while CourseHub prepares it for parsing.
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div
              className="flex h-16 w-16 items-center justify-center -[20px]"
            >
              {isDragActive ? (
                <File size={28} />
              ) : (
                <Upload size={28} />
              )}
            </div>
            <div>
              <p className="text-base font-medium">
                {isDragActive ? "Drop the file here" : "Drag and drop a file, or click to browse"}
              </p>
              <p className="text-sm mt-1.5">
                PDF, slides, images, or notes. CourseHub will sort the structure out for you.
              </p>
            </div>
            <span className="text-[11px] font-medium">Max 30 MB</span>
          </div>
        )}
      </div>
      {error && (
        <div
          className="mt-4 -[16px] px-4 py-3 text-sm"
        >
          {error}
        </div>
      )}
    </div>
  );
}
