"use client";

import { useCallback, useState } from "react";
import { useI18n } from "@/lib/i18n";

function ConfirmDialog({
  message,
  onConfirm,
  onCancel,
}: {
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  const { t } = useI18n();
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: "rgba(0,0,0,0.35)" }}
      onClick={onCancel}
    >
      <div
        className="ui-panel p-6 max-w-sm w-full"
        onClick={(e) => e.stopPropagation()}
      >
        <p className="text-sm mb-5" style={{ color: "var(--text-primary)" }}>
          {message}
        </p>
        <div className="flex justify-end gap-2">
          <button
            onClick={onCancel}
            className="px-4 py-2 rounded-xl text-sm cursor-pointer transition-colors"
            style={{ color: "var(--text-secondary)" }}
          >
            {t("misc.cancel")}
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 rounded-xl text-sm font-medium cursor-pointer transition-colors"
            style={{ backgroundColor: "var(--danger)", color: "#fff" }}
          >
            {t("misc.confirm")}
          </button>
        </div>
      </div>
    </div>
  );
}

export function useConfirm() {
  const [pending, setPending] = useState<{
    message: string;
    resolve: (v: boolean) => void;
  } | null>(null);

  const confirm = useCallback((message: string): Promise<boolean> => {
    return new Promise((resolve) => {
      setPending({ message, resolve });
    });
  }, []);

  const dialog = pending ? (
    <ConfirmDialog
      message={pending.message}
      onConfirm={() => { pending.resolve(true); setPending(null); }}
      onCancel={() => { pending.resolve(false); setPending(null); }}
    />
  ) : null;

  return { confirm, dialog };
}
