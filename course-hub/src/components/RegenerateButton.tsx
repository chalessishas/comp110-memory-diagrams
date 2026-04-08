"use client";

import { useState } from "react";
import { Languages, Loader2 } from "lucide-react";
import { useI18n } from "@/lib/i18n";

export function RegenerateButton({ courseId }: { courseId: string }) {
  const { locale } = useI18n();
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  async function handleRegenerate() {
    setLoading(true);
    const res = await fetch(`/api/courses/${courseId}/regenerate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ language: locale }),
    });
    setLoading(false);
    if (res.ok) {
      setDone(true);
      setTimeout(() => window.location.reload(), 1000);
    }
  }

  return (
    <button
      onClick={handleRegenerate}
      disabled={loading || done}
      className="ui-button-secondary !text-xs disabled:opacity-50"
      title={locale === "zh" ? "用中文重新生成所有内容" : "Regenerate all content in English"}
    >
      {loading ? (
        <Loader2 size={13} className="animate-spin" />
      ) : (
        <Languages size={13} />
      )}
      {done
        ? (locale === "zh" ? "已完成" : "Done!")
        : (locale === "zh" ? "汉化课程" : "Translate course")}
    </button>
  );
}
