"use client";

import { use, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, BookOpen } from "lucide-react";

export default function JoinPage({ params }: { params: Promise<{ token: string }> }) {
  const { token } = use(params);
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleJoin() {
    setLoading(true);
    setError(null);
    const res = await fetch("/api/courses/fork", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
    });
    const data = await res.json();
    if (res.ok) {
      router.push(`/course/${data.course_id}`);
    } else {
      setError(data.error || "Failed to join");
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div
        className="max-w-sm w-full p-8 rounded-md text-center"
        style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}
      >
        <BookOpen size={32} className="mx-auto mb-4" style={{ color: "var(--accent)" }} />
        <h1 className="text-xl font-semibold mb-2">Join Shared Course</h1>
        <p className="text-sm mb-6" style={{ color: "var(--text-secondary)" }}>
          Someone shared their course outline with you. Fork it to your account to start studying.
        </p>
        <button
          onClick={handleJoin}
          disabled={loading}
          className="w-full px-4 py-3 rounded-xl font-medium cursor-pointer disabled:opacity-50"
          style={{ backgroundColor: "var(--accent)", color: "white" }}
        >
          {loading ? <Loader2 size={16} className="animate-spin mx-auto" /> : "Fork to My Account"}
        </button>
        {error && <p className="text-xs mt-3" style={{ color: "var(--danger)" }}>{error}</p>}
      </div>
    </div>
  );
}
