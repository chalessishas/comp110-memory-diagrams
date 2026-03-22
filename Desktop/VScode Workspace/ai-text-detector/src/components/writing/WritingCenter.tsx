"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import type {
  Genre,
  ChatMessage,
  Annotation,
  WriterProfile,
  DailyTip,
  StepCard,
  AnalyzeResponse,
  GuideStepResponse,
  GuideDialogueResponse,
  ExpandResponse,
  DailyTipResponse,
  Trait,
} from "@/lib/writing/types";
import {
  loadState,
  saveState,
  createDefaultProfile,
  updateStreak,
  markDayActive,
  addAnalysisToProfile,
  incrementGenreExperience,
} from "@/lib/writing/storage";
import { selectStaticTip } from "@/lib/writing/daily-tips";
import Editor, { type EditorHandle } from "./Editor";
import ChatPanel from "./ChatPanel";
import LabPanel from "./LabPanel";

// ── Constants ──

const GENRE_LABELS: Record<Genre, string> = {
  essay: "Essay",
  article: "Article",
  academic: "Academic",
  creative: "Creative",
  business: "Business",
};

type LayoutPreset = "side" | "top" | "full";
type Tab = "chat" | "dashboard" | "lab";

// Phase state machine: welcome → conversation → writing
type Phase = "welcome" | "conversation" | "writing";

function countWords(html: string): number {
  const text = html.replace(/<[^>]*>/g, " ").trim();
  if (!text) return 0;
  return text.split(/\s+/).filter(Boolean).length;
}

function latestTraitScores(
  profile: WriterProfile
): Record<Trait, number> | null {
  const last = profile.analysisHistory[profile.analysisHistory.length - 1];
  return last?.traitScores ?? null;
}

async function apiCall<T>(body: Record<string, unknown>): Promise<T> {
  const res = await fetch("/api/writing-assist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: "Request failed" }));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json();
}

// ── Starter cards for Welcome screen ──

interface StarterCard {
  icon: string;
  title: string;
  description: string;
  action: "essay" | "creative" | "article" | "academic" | "business" | "lab" | "exercise";
}

const STARTER_CARDS: StarterCard[] = [
  {
    icon: "✍️",
    title: "Write an essay",
    description: "I'll guide you step by step with structure and feedback",
    action: "essay",
  },
  {
    icon: "🎨",
    title: "Try creative writing",
    description: "Explore narrative, character, and voice with AI coaching",
    action: "creative",
  },
  {
    icon: "📰",
    title: "Draft an article",
    description: "Learn the 5W+H structure with real-time suggestions",
    action: "article",
  },
  {
    icon: "🔬",
    title: "Explore the Writing Lab",
    description: "See why AI text feels 'cold' — and learn to write with warmth",
    action: "lab",
  },
];

// ── Main Component ──

export default function WritingCenter() {
  // Phase controls what the user sees
  const [phase, setPhase] = useState<Phase>("welcome");

  // Core state
  const [genre, setGenre] = useState<Genre>("essay");
  const [topic, setTopic] = useState("");
  const [document, setDocument] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [activeTab, setActiveTab] = useState<Tab>("chat");
  const [layoutPreset, setLayoutPreset] = useState<LayoutPreset>("side");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [profile, setProfile] = useState<WriterProfile>(() =>
    loadState()?.profile ?? createDefaultProfile()
  );
  const [hasIncrementedThisSession, setHasIncrementedThisSession] =
    useState(false);
  const [focusedAnnotationId, setFocusedAnnotationId] = useState<
    string | null
  >(null);
  const [copied, setCopied] = useState(false);

  // Daily tip
  const [dailyTip, setDailyTip] = useState<DailyTip | null>(null);
  const [showDailyTip, setShowDailyTip] = useState(true);

  // Step cards
  const [stepCards, setStepCards] = useState<StepCard[]>([]);

  // Expanded annotation
  const [expandedAnnotation, setExpandedAnnotation] = useState<{
    id: string;
    detail: string;
    suggestion?: string;
    question: string;
  } | null>(null);

  // Conventions suppression tracking
  const [previousConventionsSuppressed, setPreviousConventionsSuppressed] =
    useState(false);

  // Layout drag
  const [splitRatio, setSplitRatio] = useState(0.5);
  const containerRef = useRef<HTMLDivElement>(null);
  const isDragging = useRef(false);
  const editorRef = useRef<EditorHandle>(null);
  const sessionWordsRef = useRef(0);

  // ── Lifecycle ──

  // Check if user has a saved draft → skip welcome
  useEffect(() => {
    const saved = loadState();
    if (saved.draft.document && saved.draft.document.trim()) {
      setDocument(saved.draft.document);
      setGenre(saved.draft.genre);
      setTopic(saved.draft.topic);
      if (saved.draft.messages.length) setMessages(saved.draft.messages);
      if (saved.draft.annotations.length) setAnnotations(saved.draft.annotations);
      setPhase("writing"); // Resume where they left off
    }
    if (saved.profile) setProfile(saved.profile);
  }, []);

  // Streak on mount
  useEffect(() => {
    setProfile((prev) => updateStreak(prev));
  }, []);

  // Daily tip on mount
  useEffect(() => {
    if (!profile.preferences.showDailyTips) {
      setShowDailyTip(false);
      return;
    }
    if (profile.stats.totalAnalyses >= 3) {
      const scores = latestTraitScores(profile);
      apiCall<DailyTipResponse>({
        action: "daily-tip",
        traitScores: scores,
        analysisHistory: profile.analysisHistory.slice(-5),
      })
        .then((data) => setDailyTip(data.tip))
        .catch(() => {
          setDailyTip(selectStaticTip(scores, new Date()));
        });
    } else {
      const scores = latestTraitScores(profile);
      setDailyTip(selectStaticTip(scores, new Date()));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Guide step cards when entering writing phase with genre + topic
  useEffect(() => {
    if (phase !== "writing" || !genre || !topic || document.trim()) return;
    const experienceLevel = profile.genreExperience[genre];
    apiCall<GuideStepResponse>({
      action: "guide",
      mode: "step",
      genre,
      topic,
      experienceLevel,
    })
      .then((data) => {
        if (data.cards) setStepCards(data.cards);
      })
      .catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase, genre, topic]);

  // 60s idle detection (only in writing phase)
  useEffect(() => {
    if (phase !== "writing" || !document.trim()) return;
    const timer = setTimeout(() => {
      const idleMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content:
          "I notice you've paused — need help with anything? Feel free to ask about your writing.",
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, idleMsg]);
    }, 60000);
    return () => clearTimeout(timer);
  }, [phase, document]);

  // Word tracking for streak
  useEffect(() => {
    const wc = countWords(document);
    const delta = wc - sessionWordsRef.current;
    if (delta > 0) sessionWordsRef.current = wc;
    if (sessionWordsRef.current >= 50) {
      setProfile((prev) => markDayActive(prev));
    }
  }, [document]);

  // Auto-save (only when there's content)
  useEffect(() => {
    if (phase === "welcome") return;
    const timer = setTimeout(() => {
      saveState({
        draft: { genre, topic, document, messages, annotations, lastSaved: Date.now() },
        profile,
      });
    }, 2000);
    return () => clearTimeout(timer);
  }, [phase, document, messages, annotations, genre, topic, profile]);

  // Clear error
  useEffect(() => {
    if (!error) return;
    const timer = setTimeout(() => setError(""), 5000);
    return () => clearTimeout(timer);
  }, [error]);

  // ── Handlers ──

  function handleStarterCard(card: StarterCard) {
    if (card.action === "lab") {
      setActiveTab("lab");
      setPhase("writing");
      return;
    }
    if (card.action === "exercise" && dailyTip?.exercisePrompt) {
      setTopic(dailyTip.exercisePrompt.slice(0, 60));
      setGenre("essay");
      setPhase("conversation");
      startConversation("essay", dailyTip.exercisePrompt.slice(0, 60));
      return;
    }
    setGenre(card.action as Genre);
    setPhase("conversation");
  }

  async function startConversation(g: Genre, t?: string) {
    const greeting: ChatMessage = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: t
        ? `Great! Let's write about "${t}". What's the main point you want to make?`
        : `What would you like to write about? Give me a topic or idea, and I'll help you get started.`,
      timestamp: Date.now(),
    };
    setMessages([greeting]);
  }

  // When user enters conversation phase without a topic
  useEffect(() => {
    if (phase === "conversation" && messages.length === 0) {
      startConversation(genre);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase]);

  async function handleSendMessage(text: string) {
    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    // In conversation phase: if user provides a topic, extract it and offer to start writing
    if (phase === "conversation" && !topic && messages.length <= 2) {
      setTopic(text.slice(0, 80));
    }

    try {
      const allMessages = [...messages, userMsg];
      const data = await apiCall<GuideDialogueResponse>({
        action: "guide",
        mode: "dialogue",
        genre,
        topic: topic || text,
        document,
        messages: allMessages,
      });

      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.message,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      // After 2 exchanges in conversation phase, suggest moving to writing
      if (phase === "conversation" && allMessages.filter(m => m.role === "user").length >= 2) {
        const transitionMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: "Ready to start writing? Click the button below to open the editor, or keep chatting if you'd like to think more.",
          timestamp: Date.now(),
        };
        setTimeout(() => {
          setMessages((prev) => [...prev, transitionMsg]);
        }, 1500);
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to get response";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  async function handleAnalyze() {
    setLoading(true);
    setError("");
    try {
      const data = await apiCall<AnalyzeResponse>({
        action: "analyze",
        genre,
        document,
      });
      setAnnotations(data.annotations);
      setExpandedAnnotation(null);

      const snapshot = {
        date: new Date().toISOString().slice(0, 10),
        genre,
        wordCount: countWords(document),
        traitScores: data.traitScores,
        annotationCounts: {
          good: data.annotations.filter((a) => a.severity === "good").length,
          question: data.annotations.filter((a) => a.severity === "question").length,
          suggestion: data.annotations.filter((a) => a.severity === "suggestion").length,
          issue: data.annotations.filter((a) => a.severity === "issue").length,
        },
      };

      setProfile((prev) => {
        let updated = addAnalysisToProfile(prev, snapshot);
        if (!hasIncrementedThisSession) {
          updated = incrementGenreExperience(updated, genre);
          setHasIncrementedThisSession(true);
        }
        updated = markDayActive(updated);
        return updated;
      });

      if (previousConventionsSuppressed && !data.conventionsSuppressed) {
        const recoveryMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: "Structure looks solid now — let's fine-tune the grammar.",
          timestamp: Date.now(),
        };
        setMessages((prev) => [recoveryMsg, ...prev]);
      }
      setPreviousConventionsSuppressed(data.conventionsSuppressed);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Analysis failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  async function handleAnnotationExpand(annotationId: string) {
    const annotation = annotations.find((a) => a.id === annotationId);
    if (!annotation) return;
    try {
      const data = await apiCall<ExpandResponse>({
        action: "expand",
        annotationId,
        annotationContext: annotation,
        document,
      });
      setExpandedAnnotation({ id: annotationId, ...data });
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to expand";
      setError(msg);
    }
  }

  function handleAnnotationClickFromEditor(id: string) {
    setFocusedAnnotationId(id);
    setTimeout(() => setFocusedAnnotationId(null), 2000);
  }

  function handleAnnotationClickFromPanel(id: string) {
    editorRef.current?.scrollToAnnotation(id);
  }

  function handleStepComplete(cardId: string) {
    setStepCards((prev) =>
      prev.map((c) => (c.id === cardId ? { ...c, completed: true } : c))
    );
  }

  function handleTipTryIt(exercisePrompt: string) {
    setTopic(exercisePrompt.slice(0, 60));
    setGenre("essay");
    setPhase("writing");
    setShowDailyTip(false);
  }

  function handleTipDisable() {
    setShowDailyTip(false);
    setProfile((prev) => ({
      ...prev,
      preferences: { ...prev.preferences, showDailyTips: false },
    }));
  }

  async function handleLabRewrite(
    text: string,
    temperatures: number[]
  ): Promise<{ temperature: number; text: string; explanation: string }[]> {
    const res = await apiCall<{
      rewrites: { temperature: number; text: string; explanation: string }[];
    }>({ action: "lab-rewrite", text, temperatures });
    return res.rewrites;
  }

  function handleLabYourTurn(coldText: string, labTopic: string) {
    setDocument(`<p>${coldText}</p>`);
    setTopic(labTopic);
    setAnnotations([]);
    setStepCards([]);
    setHasIncrementedThisSession(false);
    setActiveTab("chat");
    setPhase("writing");
  }

  function handleStartWriting() {
    setPhase("writing");
  }

  // Drag handlers
  const handleDragStart = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      isDragging.current = true;
      const onMove = (ev: MouseEvent) => {
        if (!isDragging.current || !containerRef.current) return;
        const rect = containerRef.current.getBoundingClientRect();
        const ratio =
          layoutPreset === "top"
            ? (ev.clientY - rect.top) / rect.height
            : (ev.clientX - rect.left) / rect.width;
        setSplitRatio(Math.max(0.2, Math.min(0.8, ratio)));
      };
      const onUp = () => {
        isDragging.current = false;
        window.removeEventListener("mousemove", onMove);
        window.removeEventListener("mouseup", onUp);
      };
      window.addEventListener("mousemove", onMove);
      window.addEventListener("mouseup", onUp);
    },
    [layoutPreset]
  );

  function handleCopy() {
    const text = document.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();
    navigator.clipboard
      .writeText(text)
      .then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      })
      .catch(() => {});
  }

  function handleLayoutChange(preset: LayoutPreset) {
    setLayoutPreset(preset);
    setSplitRatio(0.5);
  }

  const wordCount = countWords(document);

  // ── Render ──

  // Phase 1: Welcome screen
  if (phase === "welcome") {
    return (
      <div className="flex flex-col h-full">
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="max-w-2xl w-full space-y-8">
            {/* Header */}
            <div className="text-center space-y-3">
              <h2 className="text-2xl font-semibold text-[var(--foreground)]">
                Writing Center
              </h2>
              <p className="text-[var(--muted)] text-sm max-w-md mx-auto">
                Your AI writing coach. I'll guide you through planning, drafting,
                and revising — one step at a time.
              </p>
            </div>

            {/* Daily tip (compact, above cards) */}
            {showDailyTip && dailyTip && (
              <div className="bg-[var(--card)] border border-[var(--card-border)] rounded-xl p-4 flex items-start gap-3">
                <span className="text-lg">💡</span>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-[var(--foreground)] leading-relaxed">
                    {dailyTip.tip}
                  </p>
                  {dailyTip.exercisePrompt && (
                    <button
                      onClick={() => handleTipTryIt(dailyTip.exercisePrompt!)}
                      className="mt-2 text-xs text-[var(--accent)] hover:underline font-medium"
                    >
                      Try this exercise →
                    </button>
                  )}
                </div>
                <button
                  onClick={() => setShowDailyTip(false)}
                  className="text-[var(--muted)] hover:text-[var(--foreground)] text-xs"
                >
                  ✕
                </button>
              </div>
            )}

            {/* Starter cards */}
            <div className="grid grid-cols-2 gap-3">
              {STARTER_CARDS.map((card) => (
                <button
                  key={card.action}
                  onClick={() => handleStarterCard(card)}
                  className="bg-[var(--card)] border border-[var(--card-border)] rounded-xl p-5 text-left hover:border-[var(--accent)]/40 hover:shadow-sm transition-all group"
                >
                  <span className="text-2xl block mb-3">{card.icon}</span>
                  <div className="text-sm font-medium text-[var(--foreground)] group-hover:text-[var(--accent)] transition-colors">
                    {card.title}
                  </div>
                  <div className="text-xs text-[var(--muted)] mt-1 leading-relaxed">
                    {card.description}
                  </div>
                </button>
              ))}
            </div>

            {/* Or just start typing */}
            <div className="text-center">
              <button
                onClick={() => setPhase("conversation")}
                className="text-xs text-[var(--muted)] hover:text-[var(--accent)] transition-colors"
              >
                Or just tell me what you want to write →
              </button>
            </div>

            {/* Streak */}
            {profile.streak.current > 0 && (
              <div className="text-center text-xs text-[var(--muted)]">
                🔥 {profile.streak.current}-day writing streak
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Phase 2: Conversation (AI chat only, no editor)
  if (phase === "conversation") {
    return (
      <div className="flex flex-col h-full">
        {/* Minimal header */}
        <div className="h-10 bg-[var(--card)] border-b border-[var(--card-border)] flex items-center px-4 shrink-0">
          <button
            onClick={() => {
              setPhase("welcome");
              setMessages([]);
              setTopic("");
            }}
            className="text-xs text-[var(--muted)] hover:text-[var(--foreground)] transition-colors mr-3"
          >
            ← Back
          </button>
          <span className="text-xs font-medium text-[var(--foreground)]">
            {GENRE_LABELS[genre]}
          </span>
          {topic && (
            <>
              <span className="text-xs text-[var(--muted)] mx-2">·</span>
              <span className="text-xs text-[var(--muted)] truncate">{topic}</span>
            </>
          )}
        </div>

        {/* Chat area */}
        <div className="flex-1 overflow-auto">
          <div className="max-w-2xl mx-auto p-6 space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] rounded-xl px-4 py-3 text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-[var(--accent)] text-white"
                      : "bg-[var(--card)] border border-[var(--card-border)] text-[var(--foreground)]"
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-[var(--card)] border border-[var(--card-border)] rounded-xl px-4 py-3">
                  <span className="flex gap-1">
                    <span className="w-2 h-2 bg-[var(--muted)] rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                    <span className="w-2 h-2 bg-[var(--muted)] rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                    <span className="w-2 h-2 bg-[var(--muted)] rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Bottom: input + "Start writing" button */}
        <div className="border-t border-[var(--card-border)] bg-[var(--card)] p-4 shrink-0">
          <div className="max-w-2xl mx-auto space-y-3">
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Tell me more about what you want to write..."
                className="flex-1 bg-[var(--background)] border border-[var(--card-border)] rounded-lg px-3 py-2 text-sm text-[var(--foreground)] placeholder:text-[#c4bfb7] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]/30"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    const input = e.currentTarget;
                    if (input.value.trim()) {
                      handleSendMessage(input.value.trim());
                      input.value = "";
                    }
                  }
                }}
                disabled={loading}
              />
              <button
                onClick={() => {
                  const input = globalThis.document.querySelector<HTMLInputElement>(
                    "input[placeholder*='Tell me more']"
                  );
                  if (input?.value.trim()) {
                    handleSendMessage(input.value.trim());
                    input.value = "";
                  }
                }}
                disabled={loading}
                className="bg-[var(--accent)] hover:bg-[#b5583a] disabled:bg-[#d4cfc7] text-white text-sm font-medium px-4 py-2 rounded-lg transition-all"
              >
                Send
              </button>
            </div>
            {messages.length >= 2 && (
              <button
                onClick={handleStartWriting}
                className="w-full bg-[var(--foreground)] hover:bg-[var(--foreground)]/90 text-white text-sm font-medium py-2.5 rounded-lg transition-all"
              >
                Open editor — start writing ✍️
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Phase 3: Full writing environment
  const gridStyle: React.CSSProperties =
    layoutPreset === "full"
      ? {}
      : layoutPreset === "side"
        ? { gridTemplateColumns: `${splitRatio}fr 4px ${1 - splitRatio}fr` }
        : { gridTemplateRows: `${splitRatio}fr 4px ${1 - splitRatio}fr` };

  const tabs: { key: Tab; label: string; disabled?: boolean }[] = [
    { key: "chat", label: "Chat" },
    { key: "dashboard", label: "Dashboard", disabled: true },
    { key: "lab", label: "Lab" },
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Error banner */}
      {error && (
        <div className="bg-red-50 border-b border-red-200 px-4 py-2 flex items-center gap-2 shrink-0">
          <span className="text-red-600 text-xs font-medium">{error}</span>
          <button
            onClick={() => setError("")}
            className="ml-auto text-red-400 hover:text-red-600 text-xs"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Toolbar */}
      <div className="h-10 bg-[var(--card)] border-b border-[var(--card-border)] flex items-center px-3 gap-2 shrink-0">
        <button
          onClick={() => {
            setPhase("welcome");
            setDocument("");
            setMessages([]);
            setAnnotations([]);
            setTopic("");
            setStepCards([]);
            setHasIncrementedThisSession(false);
          }}
          className="text-xs text-[var(--muted)] hover:text-[var(--foreground)] transition-colors mr-1"
          title="New writing"
        >
          ← New
        </button>

        <select
          value={genre}
          onChange={(e) => setGenre(e.target.value as Genre)}
          className="h-7 bg-[var(--background)] border border-[var(--card-border)] rounded-md text-xs text-[var(--foreground)] px-2 focus:outline-none focus:ring-1 focus:ring-[var(--accent)]/30"
        >
          {(Object.keys(GENRE_LABELS) as Genre[]).map((g) => (
            <option key={g} value={g}>
              {GENRE_LABELS[g]}
            </option>
          ))}
        </select>

        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Topic..."
          className="flex-1 h-7 bg-[var(--background)] border border-[var(--card-border)] rounded-md text-xs text-[var(--foreground)] px-2.5 placeholder:text-[#c4bfb7] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]/30 min-w-0"
        />

        <button
          onClick={handleCopy}
          title="Copy plain text"
          className="h-7 px-2.5 bg-[var(--background)] border border-[var(--card-border)] rounded-md text-xs text-[var(--muted)] hover:text-[var(--foreground)] transition-colors"
        >
          {copied ? "Copied!" : "Copy"}
        </button>

        <div className="flex items-center border border-[var(--card-border)] rounded-md overflow-hidden">
          {(["side", "top", "full"] as LayoutPreset[]).map((preset) => (
            <button
              key={preset}
              onClick={() => handleLayoutChange(preset)}
              title={preset === "side" ? "Side by side" : preset === "top" ? "Top and bottom" : "Editor only"}
              className={`h-7 w-7 flex items-center justify-center text-xs transition-colors ${
                layoutPreset === preset
                  ? "bg-[var(--accent)] text-white"
                  : "bg-[var(--background)] text-[var(--muted)] hover:text-[var(--foreground)]"
              }`}
            >
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5">
                <rect x="1" y="1" width="12" height="12" rx="1" />
                {preset === "side" && <line x1="7" y1="1" x2="7" y2="13" />}
                {preset === "top" && <line x1="1" y1="7" x2="13" y2="7" />}
              </svg>
            </button>
          ))}
        </div>
      </div>

      {/* Split pane content */}
      <div
        ref={containerRef}
        className={`flex-1 min-h-0 ${layoutPreset === "full" ? "" : "grid"}`}
        style={gridStyle}
      >
        {/* Editor pane */}
        <div className="min-h-0 min-w-0 flex flex-col bg-[var(--card)] overflow-auto">
          <div className="flex-1">
            <Editor
              ref={editorRef}
              content={document}
              onUpdate={setDocument}
              annotations={annotations}
              onAnnotationClick={handleAnnotationClickFromEditor}
            />
          </div>
          <div className="px-4 py-2 border-t border-[var(--card-border)] flex items-center gap-3">
            <button
              onClick={handleAnalyze}
              disabled={wordCount < 100 || loading}
              title={wordCount < 100 ? `Need ${100 - wordCount} more words` : "Analyze your writing"}
              className="bg-[var(--accent)] hover:bg-[#b5583a] disabled:bg-[#d4cfc7] disabled:text-[#a09a92] text-white text-xs font-medium px-4 py-1.5 rounded-md transition-all flex items-center gap-1.5"
            >
              {loading ? "Analyzing..." : "Analyze ▶"}
            </button>
            {wordCount < 100 && wordCount > 0 && (
              <span className="text-[10px] text-[var(--muted)]">
                {100 - wordCount} words to go
              </span>
            )}
          </div>
        </div>

        {/* Drag divider */}
        {layoutPreset !== "full" && (
          <div
            onMouseDown={handleDragStart}
            className={`bg-[var(--card-border)] hover:bg-[var(--accent)]/40 transition-colors ${
              layoutPreset === "side" ? "cursor-col-resize" : "cursor-row-resize"
            }`}
          />
        )}

        {/* Collaboration pane */}
        {layoutPreset !== "full" && (
          <div className="min-h-0 min-w-0 flex flex-col bg-[var(--background)] overflow-hidden">
            <div className="flex border-b border-[var(--card-border)] bg-[var(--card)] shrink-0">
              {tabs.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => !tab.disabled && setActiveTab(tab.key)}
                  disabled={tab.disabled}
                  className={`px-4 py-2.5 text-xs font-medium transition-colors relative ${
                    tab.disabled
                      ? "text-[var(--muted)]/50 cursor-not-allowed"
                      : activeTab === tab.key
                        ? "text-[var(--accent)]"
                        : "text-[var(--muted)] hover:text-[var(--foreground)]"
                  }`}
                >
                  {tab.label}
                  {activeTab === tab.key && !tab.disabled && (
                    <span className="absolute bottom-0 left-2 right-2 h-[2px] bg-[var(--accent)] rounded-full" />
                  )}
                </button>
              ))}
            </div>

            <div className="flex-1 min-h-0 overflow-auto">
              {activeTab === "chat" && (
                <ChatPanel
                  dailyTip={phase === "writing" ? dailyTip : null}
                  showDailyTip={showDailyTip && phase === "writing"}
                  onTipTryIt={handleTipTryIt}
                  onTipSkip={() => setShowDailyTip(false)}
                  onTipDisable={handleTipDisable}
                  stepCards={stepCards}
                  onStepComplete={handleStepComplete}
                  messages={messages}
                  annotations={annotations}
                  focusedAnnotationId={focusedAnnotationId}
                  expandedAnnotation={expandedAnnotation}
                  onAnnotationExpand={handleAnnotationExpand}
                  onAnnotationClick={handleAnnotationClickFromPanel}
                  onSendMessage={handleSendMessage}
                  loading={loading}
                />
              )}
              {activeTab === "dashboard" && (
                <div className="flex items-center justify-center h-full p-4 text-[var(--muted)] text-sm text-center">
                  Dashboard — Coming soon.
                </div>
              )}
              {activeTab === "lab" && (
                <LabPanel
                  onYourTurn={handleLabYourTurn}
                  loading={loading}
                  onLabRewrite={handleLabRewrite}
                />
              )}
            </div>
          </div>
        )}
      </div>

      {/* Status bar */}
      <div className="h-6 bg-[var(--accent)] flex items-center px-3 gap-3 shrink-0">
        <span className="text-white/80 text-[10px]">
          {wordCount > 0 ? `${wordCount} words` : "Ready"}
        </span>
        <span className="text-white/50 text-[10px]">{GENRE_LABELS[genre]}</span>
        {annotations.length > 0 && (
          <span className="text-white/80 text-[10px]">
            {annotations.length} annotation{annotations.length !== 1 ? "s" : ""}
          </span>
        )}
        {profile.streak.current > 0 && (
          <span className="text-white/80 text-[10px]">
            🔥 {profile.streak.current}-day streak
          </span>
        )}
      </div>
    </div>
  );
}
