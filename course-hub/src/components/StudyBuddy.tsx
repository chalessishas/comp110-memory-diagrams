"use client";

import { useRef, useEffect, useState } from "react";
import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport, isTextUIPart } from "ai";
import { MessageCircle, Send, X, Loader2, Bot } from "lucide-react";
import { useI18n } from "@/lib/i18n";

export function StudyBuddy({ courseId, courseTitle }: { courseId: string; courseTitle: string }) {
  const { t } = useI18n();
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { messages, sendMessage, status } = useChat({
    transport: new DefaultChatTransport({ api: `/api/courses/${courseId}/chat` }),
  });

  const isLoading = status === "submitted" || status === "streaming";

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function handleSubmit(e?: React.FormEvent) {
    e?.preventDefault();
    const text = input.trim();
    if (!text || isLoading) return;
    setInput("");
    sendMessage({ text });
  }

  function submitQuickQuestion(q: string) {
    if (isLoading) return;
    sendMessage({ text: q });
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full flex items-center justify-center cursor-pointer z-50 hover:scale-105 transition-transform"
        style={{
          backgroundColor: "var(--accent)",
          color: "var(--bg-surface)",
          boxShadow: "0 2px 12px var(--accent-muted)",
        }}
        title={t("misc.studyBuddy")}
      >
        <MessageCircle size={24} />
      </button>
    );
  }

  return (
    <div
      className="fixed bottom-6 right-6 w-96 h-[560px] rounded-[20px] flex flex-col z-50 overflow-hidden"
      style={{
        backgroundColor: "var(--bg-surface)",
        boxShadow: "0 8px 40px var(--accent-light), 0 2px 8px var(--accent-light)",
      }}
    >
      {/* Header — clean, no bottom border, just subtle gap */}
      <div className="flex items-center justify-between px-5 py-4">
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center"
            style={{ backgroundColor: "var(--accent-light)" }}
          >
            <Bot size={16} style={{ color: "var(--accent)" }} />
          </div>
          <div>
            <p className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>Study Buddy</p>
            <p className="text-[11px]" style={{ color: "var(--text-muted)" }}>{courseTitle}</p>
          </div>
        </div>
        <button
          onClick={() => setOpen(false)}
          className="p-2 cursor-pointer rounded-xl transition-colors"
          style={{ color: "var(--text-muted)" }}
        >
          <X size={16} />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <Bot size={32} className="mx-auto mb-3" style={{ color: "var(--text-muted)" }} />
            <p className="text-sm mb-5" style={{ color: "var(--text-muted)" }}>
              {t("studyBuddy.askAnything")}
            </p>
            <div className="space-y-2">
              {[t("studyBuddy.quickQ1"), t("studyBuddy.quickQ2"), t("studyBuddy.quickQ3")].map((q) => (
                <button
                  key={q}
                  onClick={() => submitQuickQuestion(q)}
                  className="block w-full text-left px-4 py-2.5 rounded-[12px] text-xs cursor-pointer transition-colors"
                  style={{ backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)" }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m) => {
          const textContent = m.parts
            .filter(isTextUIPart)
            .map((p) => p.text)
            .join("");

          if (!textContent) return null;

          return (
            <div key={m.id} className={`flex gap-2 ${m.role === "user" ? "justify-end" : ""}`}>
              {m.role === "assistant" && (
                <div
                  className="w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-1"
                  style={{ backgroundColor: "var(--accent-light)" }}
                >
                  <Bot size={12} style={{ color: "var(--accent)" }} />
                </div>
              )}
              <div
                className="max-w-[80%] px-4 py-3 rounded-[16px] text-sm leading-relaxed whitespace-pre-wrap"
                style={{
                  backgroundColor: m.role === "user" ? "var(--accent-light)" : "var(--bg-muted)",
                  color: m.role === "user" ? "var(--accent)" : "var(--text-primary)",
                }}
              >
                {textContent}
              </div>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex gap-2">
            <div
              className="w-6 h-6 rounded-full flex items-center justify-center shrink-0"
              style={{ backgroundColor: "var(--accent-light)" }}
            >
              <Loader2 size={12} className="animate-spin" style={{ color: "var(--accent)" }} />
            </div>
            <div
              className="px-4 py-3 rounded-[16px] text-sm"
              style={{ backgroundColor: "var(--bg-muted)", color: "var(--text-muted)" }}
            >
              {t("studyBuddy.thinking")}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input — clean, rounded, at bottom */}
      <form onSubmit={handleSubmit} className="px-4 py-3 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={t("studyBuddy.placeholder")}
          className="flex-1 px-4 py-2.5 rounded-[12px] text-sm outline-none"
          style={{
            backgroundColor: "var(--bg-surface)",
            border: "1px solid var(--border)",
            color: "var(--text-primary)",
          }}
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="p-2.5 rounded-[12px] cursor-pointer disabled:opacity-30 transition-colors"
          style={{ backgroundColor: "var(--accent)", color: "var(--bg-surface)" }}
        >
          <Send size={16} />
        </button>
      </form>
    </div>
  );
}
