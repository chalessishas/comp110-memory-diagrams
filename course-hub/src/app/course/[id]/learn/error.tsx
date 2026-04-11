"use client";

import { useEffect } from "react";
import Link from "next/link";
import { AlertTriangle } from "lucide-react";
import { useI18n } from "@/lib/i18n";

export default function LearnError({ error, reset }: { error: Error; reset: () => void }) {
  const { t } = useI18n();
  useEffect(() => {
    console.error("[LearnError]", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center py-24 gap-4 text-center">
      <AlertTriangle size={32} style={{ color: "var(--danger)" }} />
      <p className="text-base font-medium">{t("error.somethingWrong")}</p>
      <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
        {error.message || t("error.unexpected")}
      </p>
      <div className="flex gap-3 mt-2">
        <button onClick={reset} className="ui-button-primary">{t("misc.tryAgain")}</button>
        <Link href="/dashboard" className="ui-button-secondary">{t("misc.backToDashboard")}</Link>
      </div>
    </div>
  );
}
