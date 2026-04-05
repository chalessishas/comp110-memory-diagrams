"use client";

import { useI18n } from "@/lib/i18n";

export function T({ k }: { k: string }) {
  const { t } = useI18n();
  return <>{t(k)}</>;
}
