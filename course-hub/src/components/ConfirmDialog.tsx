"use client";

import { useCallback, useEffect, useRef, useState } from "react";
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
  const cancelRef = useRef<HTMLButtonElement>(null);
  const confirmRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    // Save previously focused element; restore on close
    const previouslyFocused = document.activeElement as HTMLElement | null;
    cancelRef.current?.focus();

    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") { onCancel(); return; }
      if (e.key !== "Tab") return;
      // Trap focus between cancel and confirm buttons
      const first = cancelRef.current;
      const last = confirmRef.current;
      if (e.shiftKey) {
        if (document.activeElement === first) { e.preventDefault(); last?.focus(); }
      } else {
        if (document.activeElement === last) { e.preventDefault(); first?.focus(); }
      }
    };

    window.addEventListener("keydown", handleKey);
    return () => {
      window.removeEventListener("keydown", handleKey);
      previouslyFocused?.focus();
    };
  }, [onCancel]);

  return (
    <div
      role="dialog"
      aria-modal="true"
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
            ref={cancelRef}
            onClick={onCancel}
            className="px-4 py-2 rounded-xl text-sm cursor-pointer transition-colors"
            style={{ color: "var(--text-secondary)" }}
          >
            {t("misc.cancel")}
          </button>
          <button
            ref={confirmRef}
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
