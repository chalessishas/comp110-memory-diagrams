"use client";

import { useState } from "react";
import { Share2, Copy, Check, Loader2 } from "lucide-react";

export function ShareButton({ courseId }: { courseId: string }) {
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  async function handleShare() {
    setLoading(true);
    const res = await fetch(`/api/courses/${courseId}/share`, { method: "POST" });
    const data = await res.json();
    if (data.token) {
      const url = `${window.location.origin}/join/${data.token}`;
      setShareUrl(url);
    }
    setLoading(false);
  }

  async function handleCopy() {
    if (!shareUrl) return;
    await navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  if (shareUrl) {
    return (
      <div className="flex items-center gap-1">
        <input
          readOnly
          value={shareUrl}
          className="text-[11px] px-2 py-1 rounded-lg w-48"
          style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-muted)" }}
        />
        <button onClick={handleCopy} className="p-1.5 cursor-pointer" title="Copy link">
          {copied ? <Check size={14} style={{ color: "var(--success)" }} /> : <Copy size={14} style={{ color: "var(--text-secondary)" }} />}
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={handleShare}
      disabled={loading}
      className="p-2 rounded-lg cursor-pointer"
      style={{ color: "var(--text-secondary)" }}
      title="Share course"
    >
      {loading ? <Loader2 size={18} className="animate-spin" /> : <Share2 size={18} />}
    </button>
  );
}
