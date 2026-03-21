"use client";

import { useState } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import type { AnalysisResult } from "@/lib/analysis";
import type { HumanizeResult } from "@/app/api/humanize/route";
import { PROMPT_TEMPLATES, type PromptStyle } from "@/lib/prompts";

const HumanizeDashboard = dynamic(
  () => import("@/components/HumanizeDashboard"),
  { ssr: false, loading: () => <PanelSkeleton /> }
);
const FeatureOverview = dynamic(
  () => import("@/components/FeatureOverview"),
  { ssr: false, loading: () => <PanelSkeleton /> }
);
const GLTROverlay = dynamic(() => import("@/components/GLTROverlay"), {
  ssr: false,
  loading: () => <PanelSkeleton />,
});
const PerplexityCurve = dynamic(
  () => import("@/components/PerplexityCurve"),
  { ssr: false, loading: () => <PanelSkeleton /> }
);
const EntropyChart = dynamic(() => import("@/components/EntropyChart"), {
  ssr: false,
  loading: () => <PanelSkeleton />,
});
const BurstinessChart = dynamic(
  () => import("@/components/BurstinessChart"),
  { ssr: false, loading: () => <PanelSkeleton /> }
);
const SlidingWindowChart = dynamic(
  () => import("@/components/SlidingWindowChart"),
  { ssr: false, loading: () => <PanelSkeleton /> }
);
const SentenceAnalysis = dynamic(
  () => import("@/components/SentenceAnalysis"),
  { ssr: false, loading: () => <PanelSkeleton /> }
);

function PanelSkeleton() {
  return (
    <div className="bg-[var(--card)] rounded-xl p-5 border border-[var(--card-border)] h-[360px] animate-pulse">
      <div className="h-4 w-36 bg-[#ece7df] rounded mb-4" />
      <div className="h-3 w-56 bg-[#ece7df] rounded mb-6" />
      <div className="h-[260px] bg-[#f5f1eb] rounded-lg" />
    </div>
  );
}

// ── Sidebar config ──

type Panel = "detect" | "humanize" | "writing";

const panels: { key: Panel; icon: React.ReactNode; label: string }[] = [
  {
    key: "detect",
    label: "AI Detector",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>
    ),
  },
  {
    key: "humanize",
    label: "Humanizer",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 20h9" />
        <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
      </svg>
    ),
  },
  {
    key: "writing",
    label: "Writing Center",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
        <polyline points="10 9 9 9 8 9" />
      </svg>
    ),
  },
];

// ── Detect tabs ──

const detectTabs = [
  { key: "overview", label: "Overview", icon: "◎" },
  { key: "sentences", label: "Sentences", icon: "≡" },
  { key: "gltr", label: "GLTR", icon: "▦" },
  { key: "perplexity", label: "Perplexity", icon: "〰" },
  { key: "entropy", label: "Entropy", icon: "◆" },
  { key: "burstiness", label: "Burstiness", icon: "▥" },
  { key: "window", label: "Window", icon: "◳" },
] as const;

type DetectTab = (typeof detectTabs)[number]["key"];

// ── Main ──

export default function AppShell() {
  const [activePanel, setActivePanel] = useState<Panel>("detect");
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Detect
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [activeTab, setActiveTab] = useState<DetectTab>("overview");

  // Humanize
  const [humanizeResult, setHumanizeResult] = useState<HumanizeResult | null>(null);
  const [copied, setCopied] = useState(false);

  // Writing Center
  const [promptStyle, setPromptStyle] = useState<PromptStyle>("essay");
  const [topic, setTopic] = useState("");
  const [generatedPrompt, setGeneratedPrompt] = useState("");

  async function handleAnalyze() {
    if (!text.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text.trim() }),
      });
      const data = await res.json();
      if (!res.ok) { setError(data.error || "Analysis failed"); return; }
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Network error");
    } finally {
      setLoading(false);
    }
  }

  async function handleHumanize() {
    if (!text.trim()) return;
    setLoading(true);
    setError("");
    setHumanizeResult(null);
    try {
      const res = await fetch("/api/humanize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text.trim() }),
      });
      const data = await res.json();
      if (!res.ok) { setError(data.error || "Humanization failed"); return; }
      setHumanizeResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Network error");
    } finally {
      setLoading(false);
    }
  }

  function scoreColor(s: number) {
    if (s > 70) return "text-[#c44]";
    if (s > 30) return "text-amber-600";
    return "text-emerald-600";
  }
  function scoreBg(s: number) {
    if (s > 70) return "bg-red-50 border-red-200";
    if (s > 30) return "bg-amber-50 border-amber-200";
    return "bg-emerald-50 border-emerald-200";
  }
  function scoreLabel(s: number) {
    if (s > 70) return "Likely AI-generated";
    if (s > 30) return "Inconclusive";
    return "Likely Human-written";
  }

  function renderDetectChart() {
    if (!result) return null;
    switch (activeTab) {
      case "overview": return <FeatureOverview result={result} />;
      case "sentences": return <SentenceAnalysis sentenceScores={result.sentenceScores} />;
      case "gltr": return <GLTROverlay tokens={result.tokens} gltr={result.gltr} />;
      case "perplexity": return <PerplexityCurve tokens={result.tokens} />;
      case "entropy": return <EntropyChart tokens={result.tokens} stats={result.entropy} />;
      case "burstiness": return <BurstinessChart sentences={result.sentences} />;
      case "window": return <SlidingWindowChart data={result.slidingWindow} />;
    }
  }

  return (
    <div className="h-screen flex overflow-hidden bg-[var(--background)]">
      {/* ── Activity Bar (VSCode-style) ── */}
      <div className="w-[52px] bg-[#2d2b28] flex flex-col items-center py-3 gap-1 shrink-0">
        {panels.map((p) => (
          <button
            key={p.key}
            onClick={() => setActivePanel(p.key)}
            title={p.label}
            className={`w-10 h-10 flex items-center justify-center rounded-lg transition-all relative group ${
              activePanel === p.key
                ? "text-white bg-white/10"
                : "text-white/40 hover:text-white/70"
            }`}
          >
            {p.icon}
            {activePanel === p.key && (
              <span className="absolute left-0 top-1.5 bottom-1.5 w-[2px] bg-[var(--accent)] rounded-r" />
            )}
            <span className="absolute left-12 px-2 py-1 bg-[#1e1d1b] text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap transition-opacity z-50">
              {p.label}
            </span>
          </button>
        ))}

        <div className="flex-1" />

        <Link
          href="/blog"
          title="Dev Log"
          className="w-10 h-10 flex items-center justify-center rounded-lg text-white/40 hover:text-white/70 transition-all relative group"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
          </svg>
          <span className="absolute left-12 px-2 py-1 bg-[#1e1d1b] text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap transition-opacity z-50">
            Dev Log
          </span>
        </Link>

        <div className="w-6 h-6 rounded-full bg-[var(--accent)] flex items-center justify-center">
          <span className="text-white text-[10px] font-bold">X</span>
        </div>
      </div>

      {/* ── Main Area ── */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Title bar */}
        <div className="h-10 bg-[#3a3836] flex items-center px-4 shrink-0">
          <span className="text-white/60 text-xs font-medium">
            AI Text X-Ray
          </span>
          <span className="text-white/30 text-xs mx-2">/</span>
          <span className="text-white/90 text-xs font-medium">
            {panels.find((p) => p.key === activePanel)?.label}
          </span>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {error && (
            <div className="mx-6 mt-4 bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-red-700 text-sm">
              {error}
            </div>
          )}

          {activePanel === "detect" && (
            <DetectPanel
              text={text}
              setText={setText}
              loading={loading}
              result={result}
              activeTab={activeTab}
              setActiveTab={setActiveTab}
              onAnalyze={handleAnalyze}
              scoreColor={scoreColor}
              scoreBg={scoreBg}
              scoreLabel={scoreLabel}
              renderChart={renderDetectChart}
            />
          )}

          {activePanel === "humanize" && (
            <HumanizePanel
              text={text}
              setText={setText}
              loading={loading}
              humanizeResult={humanizeResult}
              onHumanize={handleHumanize}
            />
          )}

          {activePanel === "writing" && (
            <WritingPanel
              promptStyle={promptStyle}
              setPromptStyle={setPromptStyle}
              topic={topic}
              setTopic={setTopic}
              generatedPrompt={generatedPrompt}
              setGeneratedPrompt={setGeneratedPrompt}
              copied={copied}
              setCopied={setCopied}
            />
          )}
        </div>

        {/* Status bar */}
        <div className="h-6 bg-[var(--accent)] flex items-center px-3 shrink-0">
          <span className="text-white/80 text-[10px]">
            {text.trim() ? `${text.trim().split(/\s+/).filter(Boolean).length} words` : "Ready"}
          </span>
          {result && (
            <span className="text-white/80 text-[10px] ml-3">
              Perplexity: {result.overallPerplexity.toFixed(2)} · {result.tokens.length} tokens
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Detect Panel ──

function DetectPanel({
  text, setText, loading, result, activeTab, setActiveTab, onAnalyze,
  scoreColor, scoreBg, scoreLabel, renderChart,
}: {
  text: string;
  setText: (t: string) => void;
  loading: boolean;
  result: AnalysisResult | null;
  activeTab: DetectTab;
  setActiveTab: (t: DetectTab) => void;
  onAnalyze: () => void;
  scoreColor: (s: number) => string;
  scoreBg: (s: number) => string;
  scoreLabel: (s: number) => string;
  renderChart: () => React.ReactNode;
}) {
  return (
    <div className="p-6 flex flex-col lg:flex-row gap-6 lg:items-start">
      {/* Left: Input + Score */}
      <div className="lg:w-[440px] lg:shrink-0 space-y-4">
        <div className="bg-[var(--card)] rounded-xl border border-[var(--card-border)] shadow-sm">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste text here to analyze..."
            rows={16}
            className="w-full bg-transparent text-[var(--foreground)] text-sm leading-relaxed placeholder:text-[#c4bfb7] focus:outline-none resize-y min-h-[300px] p-5"
          />
          <div className="flex items-center justify-between px-5 py-3 border-t border-[var(--card-border)]">
            <span className="text-xs text-[var(--muted)]">
              {text.trim().split(/\s+/).filter(Boolean).length} words
            </span>
            <button
              onClick={onAnalyze}
              disabled={loading || !text.trim()}
              className="bg-[var(--accent)] hover:bg-[#b5583a] disabled:bg-[#d4cfc7] disabled:text-[#a09a92] text-white text-sm font-medium px-5 py-2 rounded-lg transition-all"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Analyzing...
                </span>
              ) : "Analyze"}
            </button>
          </div>
        </div>

        {result && result.scoringEligible && (
          <div className={`rounded-xl p-4 border ${scoreBg(result.overallScore)}`}>
            <div className="flex items-center gap-4">
              <div className="text-center min-w-[60px]">
                <div className={`text-2xl font-bold tracking-tight ${scoreColor(result.overallScore)}`}>
                  {result.overallScore.toFixed(0)}%
                </div>
                <div className="text-[10px] text-[var(--muted)]">AI Score</div>
              </div>
              <div className="border-l border-current/10 pl-4">
                <div className={`text-sm font-semibold ${scoreColor(result.overallScore)}`}>
                  {scoreLabel(result.overallScore)}
                </div>
                <div className="text-xs text-[var(--muted)] mt-0.5">
                  {result.classification ? (
                    <>
                      Class: {result.classification.label_name} · Perplexity: {result.overallPerplexity.toFixed(2)} · {result.wordCount} words
                    </>
                  ) : (
                    <>
                      Perplexity: {result.overallPerplexity.toFixed(2)} · {result.tokens.length} tokens · {result.wordCount} words
                    </>
                  )}
                </div>
                {result.classification && (
                  <div className="flex gap-2 mt-1.5">
                    {Object.entries(result.classification.probabilities).map(([name, prob]) => (
                      <span key={name} className={`text-[10px] px-1.5 py-0.5 rounded ${
                        name === result.classification!.label_name
                          ? "bg-[var(--foreground)]/10 font-semibold"
                          : "text-[var(--muted)]"
                      }`}>
                        {name}: {(prob * 100).toFixed(0)}%
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {result && !result.scoringEligible && (
          <div className="rounded-xl p-4 border bg-amber-50 border-amber-200">
            <div className="text-sm font-semibold text-amber-700">Insufficient text for scoring</div>
            <div className="text-xs text-amber-600 mt-1">
              300+ words required ({result.wordCount} provided). Feature analysis shown without overall score.
            </div>
          </div>
        )}
      </div>

      {/* Right: Charts */}
      <div className="flex-1 min-w-0">
        <div className="bg-[var(--card)] rounded-xl border border-[var(--card-border)] shadow-sm overflow-hidden">
          <div className="flex border-b border-[var(--card-border)] overflow-x-auto">
            {detectTabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex-1 min-w-[72px] px-2.5 py-3 text-xs font-medium transition-colors relative whitespace-nowrap ${
                  activeTab === tab.key
                    ? "text-[var(--accent)]"
                    : "text-[var(--muted)] hover:text-[var(--foreground)]"
                }`}
              >
                <span className="flex items-center justify-center gap-1">
                  <span className="text-sm">{tab.icon}</span>
                  {tab.label}
                </span>
                {activeTab === tab.key && (
                  <span className="absolute bottom-0 left-2 right-2 h-[2px] bg-[var(--accent)] rounded-full" />
                )}
              </button>
            ))}
          </div>
          <div className="p-5">
            {result ? renderChart() : (
              <div className="h-[360px] flex items-center justify-center text-[var(--muted)] text-sm">
                {loading ? (
                  <div className="flex flex-col items-center gap-3">
                    <span className="w-7 h-7 border-2 border-[var(--accent)]/30 border-t-[var(--accent)] rounded-full animate-spin" />
                    <span>Analyzing text...</span>
                  </div>
                ) : "Paste text and click Analyze to see results"}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Humanize Panel ──

function HumanizePanel({
  text, setText, loading, humanizeResult, onHumanize,
}: {
  text: string;
  setText: (t: string) => void;
  loading: boolean;
  humanizeResult: HumanizeResult | null;
  onHumanize: () => void;
}) {
  return (
    <div className="p-6 flex flex-col lg:flex-row gap-6 lg:items-start">
      <div className="lg:w-[440px] lg:shrink-0">
        <div className="bg-[var(--card)] rounded-xl border border-[var(--card-border)] shadow-sm">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste AI-generated text to humanize..."
            rows={16}
            className="w-full bg-transparent text-[var(--foreground)] text-sm leading-relaxed placeholder:text-[#c4bfb7] focus:outline-none resize-y min-h-[300px] p-5"
          />
          <div className="flex items-center justify-between px-5 py-3 border-t border-[var(--card-border)]">
            <span className="text-xs text-[var(--muted)]">
              {text.trim().split(/\s+/).filter(Boolean).length} words
            </span>
            <button
              onClick={onHumanize}
              disabled={loading || !text.trim()}
              className="bg-emerald-600 hover:bg-emerald-700 disabled:bg-[#d4cfc7] disabled:text-[#a09a92] text-white text-sm font-medium px-5 py-2 rounded-lg transition-all"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Humanizing...
                </span>
              ) : "Humanize"}
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 min-w-0">
        {humanizeResult ? (
          <HumanizeDashboard result={humanizeResult} />
        ) : (
          <div className="bg-[var(--card)] rounded-xl border border-[var(--card-border)] shadow-sm">
            <div className="h-[360px] flex items-center justify-center text-[var(--muted)] text-sm">
              {loading ? (
                <div className="flex flex-col items-center gap-3">
                  <span className="w-7 h-7 border-2 border-emerald-300/50 border-t-emerald-500 rounded-full animate-spin" />
                  <span>Running humanization methods...</span>
                </div>
              ) : "Paste AI text and click Humanize to see sentence dashboard"}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Writing Center Panel ──

function WritingPanel({
  promptStyle, setPromptStyle, topic, setTopic,
  generatedPrompt, setGeneratedPrompt, copied, setCopied,
}: {
  promptStyle: PromptStyle;
  setPromptStyle: (s: PromptStyle) => void;
  topic: string;
  setTopic: (t: string) => void;
  generatedPrompt: string;
  setGeneratedPrompt: (p: string) => void;
  copied: boolean;
  setCopied: (c: boolean) => void;
}) {
  function handleGenerate() {
    if (!topic.trim()) return;
    setGeneratedPrompt(PROMPT_TEMPLATES[promptStyle].replace("{topic}", topic.trim()));
  }

  function handleCopy() {
    navigator.clipboard.writeText(generatedPrompt).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }).catch(() => {});
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-lg font-semibold text-[var(--foreground)]">Writing Center</h2>
        <p className="text-sm text-[var(--muted)] mt-1">
          Generate optimized prompts that produce AI text matching our human corpus style — making humanization much more effective.
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Left: Config */}
        <div className="lg:w-[360px] lg:shrink-0 space-y-4">
          <div className="bg-[var(--card)] rounded-xl border border-[var(--card-border)] shadow-sm p-5 space-y-4">
            <div>
              <label className="text-xs font-medium text-[var(--muted)] uppercase tracking-wide">
                Topic
              </label>
              <textarea
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., The impact of social media on teenage mental health"
                rows={4}
                className="w-full mt-1.5 bg-[#faf8f5] rounded-lg p-3 text-sm text-[var(--foreground)] placeholder:text-[#c4bfb7] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]/20 resize-none"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-[var(--muted)] uppercase tracking-wide">
                Writing Style
              </label>
              <div className="grid grid-cols-2 gap-2 mt-1.5">
                {(Object.keys(PROMPT_TEMPLATES) as PromptStyle[]).map((style) => (
                  <button
                    key={style}
                    onClick={() => setPromptStyle(style)}
                    className={`px-3 py-2 text-sm rounded-lg border transition-all capitalize ${
                      promptStyle === style
                        ? "border-[var(--accent)] bg-[var(--accent)]/5 text-[var(--accent)] font-medium"
                        : "border-[var(--card-border)] text-[var(--muted)] hover:border-[var(--accent)]/30"
                    }`}
                  >
                    {style}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handleGenerate}
              disabled={!topic.trim()}
              className="w-full bg-[#2d2b28] hover:bg-[#3a3836] disabled:bg-[#d4cfc7] disabled:text-[#a09a92] text-white text-sm font-medium py-2.5 rounded-lg transition-all"
            >
              Generate Prompt
            </button>
          </div>

          {/* Workflow hint */}
          <div className="bg-[#f5f1eb] rounded-xl p-4 space-y-2">
            <div className="text-xs font-semibold text-[var(--foreground)]">Workflow</div>
            <div className="space-y-1.5">
              {[
                { n: "1", text: "Generate a style-optimized prompt here", active: true },
                { n: "2", text: "Paste it into ChatGPT / Claude", active: false },
                { n: "3", text: "Bring the output to Humanizer", active: false },
                { n: "4", text: "Verify with AI Detector", active: false },
              ].map((step) => (
                <div key={step.n} className="flex items-center gap-2">
                  <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                    step.active ? "bg-[var(--accent)] text-white" : "bg-[var(--card-border)] text-[var(--muted)]"
                  }`}>
                    {step.n}
                  </span>
                  <span className={`text-xs ${step.active ? "text-[var(--foreground)]" : "text-[var(--muted)]"}`}>
                    {step.text}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Output */}
        <div className="flex-1 min-w-0">
          <div className="bg-[var(--card)] rounded-xl border border-[var(--card-border)] shadow-sm overflow-hidden">
            <div className="px-5 py-3 border-b border-[var(--card-border)] flex items-center justify-between">
              <span className="text-xs font-semibold text-[var(--foreground)]">
                Generated Prompt
              </span>
              {generatedPrompt && (
                <button
                  onClick={handleCopy}
                  className="bg-[#2d2b28] hover:bg-[#3a3836] text-white text-xs font-medium px-3 py-1.5 rounded-lg transition-all"
                >
                  {copied ? "Copied!" : "Copy"}
                </button>
              )}
            </div>
            <div className="p-5">
              {generatedPrompt ? (
                <pre className="bg-[#faf8f5] rounded-lg p-4 text-sm text-[var(--foreground)] whitespace-pre-wrap leading-relaxed max-h-[500px] overflow-y-auto font-[inherit]">
                  {generatedPrompt}
                </pre>
              ) : (
                <div className="h-[360px] flex flex-col items-center justify-center text-[var(--muted)] text-sm gap-2">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" opacity="0.4">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                  </svg>
                  <p>Enter a topic and select a style</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
