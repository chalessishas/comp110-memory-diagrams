"use client";

import { useRef, useEffect, useState } from "react";
import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport, isTextUIPart } from "ai";
import { MessageCircle, Send, X, Loader2, Bot } from "lucide-react";

export function StudyBuddy({ courseId, courseTitle }: { courseId: string; courseTitle: string }) {
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
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full flex items-center justify-center cursor-pointer z-50"
        style={{ backgroundColor: "var(--accent)", color: "white" }}
        title="Study Buddy"
      >
        <MessageCircle size={24} />
      </button>
    );
  }

  return (
    <div
      className="fixed bottom-6 right-6 w-96 h-[560px] rounded-md flex flex-col z-50 overflow-hidden"
      style={{
        backgroundColor: "var(--bg-surface)",
        border: "1px solid var(--border)",
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4" style={{ borderBottom: "1px solid var(--border)" }}>
        <div className="flex items-center gap-2">
          <Bot size={18} style={{ color: "var(--accent)" }} />
          <div>
            <p className="text-sm font-medium">Study Buddy</p>
            <p className="text-[11px]" style={{ color: "var(--text-secondary)" }}>{courseTitle}</p>
          </div>
        </div>
        <button onClick={() => setOpen(false)} className="p-1 cursor-pointer rounded-lg hover:bg-black/5">
          <X size={16} style={{ color: "var(--text-secondary)" }} />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <Bot size={32} className="mx-auto mb-3" style={{ color: "var(--border)" }} />
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
              Ask me anything about this course
            </p>
            <div className="mt-4 space-y-2">
              {["What are the key topics?", "Explain the hardest concept", "Help me prepare for the exam"].map((q) => (
                <button
                  key={q}
                  onClick={() => submitQuickQuestion(q)}
                  className="block w-full text-left px-3 py-2 rounded-xl text-xs cursor-pointer"
                  style={{ backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)", border: "1px solid var(--border)" }}
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
                <div className="w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-1" style={{ backgroundColor: "var(--bg-muted)" }}>
                  <Bot size={12} style={{ color: "var(--text-secondary)" }} />
                </div>
              )}
              <div
                className="max-w-[80%] px-3.5 py-2.5 rounded-md text-sm leading-relaxed whitespace-pre-wrap"
                style={{
                  backgroundColor: m.role === "user" ? "var(--accent)" : "var(--bg-muted)",
                  color: m.role === "user" ? "white" : "var(--text-primary)",
                }}
              >
                {textContent}
              </div>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex gap-2">
            <div className="w-6 h-6 rounded-full flex items-center justify-center shrink-0" style={{ backgroundColor: "var(--bg-muted)" }}>
              <Loader2 size={12} className="animate-spin" style={{ color: "var(--text-secondary)" }} />
            </div>
            <div className="px-3.5 py-2.5 rounded-md text-sm" style={{ backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)" }}>
              Thinking...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form
        onSubmit={handleSubmit}
        className="px-4 py-3 flex gap-2"
        style={{ borderTop: "1px solid var(--border)" }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about this course..."
          className="flex-1 px-3.5 py-2.5 rounded-xl text-sm outline-none"
          style={{ backgroundColor: "var(--bg-muted)", border: "1px solid var(--border)" }}
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="p-2.5 rounded-xl cursor-pointer disabled:opacity-30"
          style={{ backgroundColor: "var(--accent)", color: "white" }}
        >
          <Send size={16} />
        </button>
      </form>
    </div>
  );
}
