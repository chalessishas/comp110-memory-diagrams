"use client";

import { useEffect } from "react";
import Link from "next/link";
import { AlertTriangle } from "lucide-react";

export default function CourseError({ error, reset }: { error: Error; reset: () => void }) {
  useEffect(() => {
    console.error("[CourseError]", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center py-24 gap-4 text-center">
      <AlertTriangle size={32} style={{ color: "var(--danger)" }} />
      <p className="text-base font-medium">Something went wrong</p>
      <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
        {error.message || "An unexpected error occurred."}
      </p>
      <div className="flex gap-3 mt-2">
        <button onClick={reset} className="ui-button-primary">Try again</button>
        <Link href="/dashboard" className="ui-button-secondary">Back to Dashboard</Link>
      </div>
    </div>
  );
}
