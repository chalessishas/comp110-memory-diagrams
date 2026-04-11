"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Languages, Loader2 } from "lucide-react";
import { useI18n } from "@/lib/i18n";

export function RegenerateButton({ courseId }: { courseId: string }) {
  const router = useRouter();
  const { t, locale } = useI18n();
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
      setTimeout(() => router.refresh(), 1000);
    }
  }

  return (
    <button
      onClick={handleRegenerate}
      disabled={loading || done}
      className="ui-button-secondary !text-xs disabled:opacity-50"
      title={t("regenerate.title")}
    >
      {loading ? (
        <Loader2 size={13} className="animate-spin" />
      ) : (
        <Languages size={13} />
      )}
      {done ? t("regenerate.done") : t("regenerate.translate")}
    </button>
  );
}
