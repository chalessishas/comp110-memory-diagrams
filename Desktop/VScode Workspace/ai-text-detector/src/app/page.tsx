import Link from "next/link";
import { getAllPosts, type PostMeta } from "@/lib/posts";

function NavBar() {
  return (
    <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-[var(--card-border)]">
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-[var(--accent)] flex items-center justify-center">
            <span className="text-white text-xs font-bold">X</span>
          </div>
          <span className="text-sm font-semibold text-[var(--foreground)]">
            AI Text X-Ray
          </span>
        </Link>
        <div className="flex items-center gap-1">
          <Link
            href="/app"
            className="px-3 py-1.5 text-xs font-medium text-[var(--muted)] hover:text-[var(--foreground)] transition-colors rounded-lg"
          >
            AI Detector
          </Link>
          <Link
            href="/app"
            className="px-3 py-1.5 text-xs font-medium text-[var(--muted)] hover:text-[var(--foreground)] transition-colors rounded-lg"
          >
            Humanizer
          </Link>
          <Link
            href="/app"
            className="px-3 py-1.5 text-xs font-medium text-[var(--muted)] hover:text-[var(--foreground)] transition-colors rounded-lg"
          >
            Writing Center
          </Link>
          <Link
            href="/blog"
            className="px-3 py-1.5 text-xs font-medium text-[var(--muted)] hover:text-[var(--foreground)] transition-colors rounded-lg"
          >
            Blog
          </Link>
          <Link
            href="/app"
            className="ml-2 px-4 py-1.5 text-xs font-medium bg-[var(--accent)] text-white rounded-lg hover:bg-[#b5583a] transition-colors"
          >
            Get Started
          </Link>
        </div>
      </div>
    </nav>
  );
}

function Hero() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-3xl mx-auto text-center space-y-6">
        <h1 className="text-4xl font-bold text-[var(--foreground)] tracking-tight leading-tight">
          Detect AI text. Humanize it.
          <br />
          <span className="text-[var(--accent)]">Learn to write better.</span>
        </h1>
        <p className="text-lg text-[var(--muted)] max-w-xl mx-auto leading-relaxed">
          AI Text X-Ray goes beyond a simple score — it shows you{" "}
          <em>exactly why</em> text looks AI-generated, helps you rewrite it,
          and teaches you to write with authentic voice.
        </p>
        <div className="flex items-center justify-center gap-3 pt-2">
          <Link
            href="/app"
            className="px-6 py-2.5 bg-[var(--accent)] text-white text-sm font-medium rounded-xl hover:bg-[#b5583a] transition-colors shadow-sm"
          >
            Try it free →
          </Link>
          <a
            href="#how-it-works"
            className="px-6 py-2.5 text-sm font-medium text-[var(--foreground)] border border-[var(--card-border)] rounded-xl hover:border-[var(--accent)]/40 transition-colors"
          >
            How it works
          </a>
        </div>
      </div>
    </section>
  );
}

function ToolCards() {
  const tools = [
    {
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
      ),
      title: "AI Detector",
      description:
        "Paste any text and see a detailed breakdown — perplexity curves, GLTR token ranks, entropy patterns, sentence-level scoring. Not just a number, but the evidence behind it.",
      color: "text-blue-600 bg-blue-50 border-blue-200",
      cta: "Detect text",
    },
    {
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 20h9" />
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
        </svg>
      ),
      title: "Humanizer",
      description:
        "Transform AI-generated text using a 50-million sentence human corpus. 11 replacement strategies — from full sentence swaps to subtle phrase adjustments. Choose the method that fits.",
      color: "text-emerald-600 bg-emerald-50 border-emerald-200",
      cta: "Humanize text",
    },
    {
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" y1="13" x2="8" y2="13" />
          <line x1="16" y1="17" x2="8" y2="17" />
        </svg>
      ),
      title: "Writing Center",
      description:
        "Your AI writing coach. Get guided through brainstorming, outlining, drafting, and revising — with feedback based on the 6+1 Traits framework used by writing teachers worldwide.",
      color: "text-purple-600 bg-purple-50 border-purple-200",
      cta: "Start writing",
    },
  ];

  return (
    <section className="py-16 px-6">
      <div className="max-w-5xl mx-auto">
        <h2 className="text-xl font-semibold text-[var(--foreground)] text-center mb-10">
          Three tools, one platform
        </h2>
        <div className="grid md:grid-cols-3 gap-5">
          {tools.map((tool) => (
            <Link
              key={tool.title}
              href="/app"
              className="bg-[var(--card)] border border-[var(--card-border)] rounded-2xl p-6 hover:border-[var(--accent)]/40 hover:shadow-md transition-all group"
            >
              <div
                className={`w-10 h-10 rounded-xl flex items-center justify-center border ${tool.color} mb-4`}
              >
                {tool.icon}
              </div>
              <h3 className="text-base font-semibold text-[var(--foreground)] group-hover:text-[var(--accent)] transition-colors">
                {tool.title}
              </h3>
              <p className="text-sm text-[var(--muted)] mt-2 leading-relaxed">
                {tool.description}
              </p>
              <span className="inline-block mt-4 text-xs font-medium text-[var(--accent)] group-hover:underline">
                {tool.cta} →
              </span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

function HowItWorks() {
  const signals = [
    { name: "Perplexity", ai: "3-8", human: "20-50", description: "How predictable is each word?" },
    { name: "GLTR Rank", ai: ">90% top-10", human: "<75% top-10", description: "Does the model's top prediction always match?" },
    { name: "Entropy", ai: "1.0-2.0", human: "2.5-3.5", description: "How uncertain is the model at each position?" },
    { name: "Burstiness", ai: "0.10-0.20", human: "0.35-0.65", description: "Do sentence lengths vary?" },
    { name: "Vocabulary", ai: "0.65-0.80 TTR", human: "0.75-0.90 TTR", description: "How rich is the word choice?" },
  ];

  return (
    <section id="how-it-works" className="py-16 px-6 bg-[var(--card)]">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-xl font-semibold text-[var(--foreground)] text-center mb-3">
          How detection works
        </h2>
        <p className="text-sm text-[var(--muted)] text-center mb-10 max-w-lg mx-auto">
          We analyze 5 independent signals. Any single one can be fooled — but
          defeating all 5 simultaneously is extremely difficult.
        </p>
        <div className="space-y-3">
          {signals.map((s) => (
            <div
              key={s.name}
              className="flex items-center gap-4 bg-[var(--background)] rounded-xl p-4 border border-[var(--card-border)]"
            >
              <div className="w-28 shrink-0">
                <div className="text-sm font-semibold text-[var(--foreground)]">
                  {s.name}
                </div>
                <div className="text-[10px] text-[var(--muted)] mt-0.5">
                  {s.description}
                </div>
              </div>
              <div className="flex-1 flex items-center gap-3">
                <div className="flex-1 bg-red-50 border border-red-200 rounded-lg px-3 py-2 text-center">
                  <div className="text-[10px] text-red-400 font-medium">AI</div>
                  <div className="text-xs text-red-600 font-semibold mt-0.5">
                    {s.ai}
                  </div>
                </div>
                <div className="text-[var(--muted)] text-xs">vs</div>
                <div className="flex-1 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2 text-center">
                  <div className="text-[10px] text-emerald-400 font-medium">
                    Human
                  </div>
                  <div className="text-xs text-emerald-600 font-semibold mt-0.5">
                    {s.human}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Stats() {
  const stats = [
    { value: "50M", label: "Human sentences in corpus" },
    { value: "5", label: "Independent detection signals" },
    { value: "11", label: "Humanization strategies" },
    { value: "7", label: "Writing trait dimensions" },
  ];

  return (
    <section className="py-16 px-6">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-xl font-semibold text-[var(--foreground)] text-center mb-10">
          Built on real data
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map((s) => (
            <div
              key={s.label}
              className="bg-[var(--card)] border border-[var(--card-border)] rounded-xl p-5 text-center"
            >
              <div className="text-2xl font-bold text-[var(--accent)]">
                {s.value}
              </div>
              <div className="text-xs text-[var(--muted)] mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function WhatMakesUsDifferent() {
  const points = [
    {
      title: "We show our work",
      description:
        "Other detectors give you a number. We give you interactive charts showing exactly which sentences triggered detection and why. You see the evidence.",
    },
    {
      title: "Corpus-based humanization",
      description:
        "We don't paraphrase with AI (that's detectable too). We match your text against 50 million real human sentences and swap in genuine human writing.",
    },
    {
      title: "Writing education, not just detection",
      description:
        "Our Writing Center teaches the 6+1 Traits framework used by educators worldwide. We don't just tell you what's wrong — we help you get better.",
    },
    {
      title: "Free and transparent",
      description:
        "No hidden algorithms. No paywall for basic features. We believe in open, explainable AI analysis.",
    },
  ];

  return (
    <section className="py-16 px-6 bg-[var(--card)]">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-xl font-semibold text-[var(--foreground)] text-center mb-10">
          What makes us different
        </h2>
        <div className="grid md:grid-cols-2 gap-5">
          {points.map((p) => (
            <div
              key={p.title}
              className="bg-[var(--background)] rounded-xl p-5 border border-[var(--card-border)]"
            >
              <h3 className="text-sm font-semibold text-[var(--foreground)]">
                {p.title}
              </h3>
              <p className="text-xs text-[var(--muted)] mt-2 leading-relaxed">
                {p.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function BlogPreview({ posts }: { posts: PostMeta[] }) {
  if (posts.length === 0) return null;

  return (
    <section className="py-16 px-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-xl font-semibold text-[var(--foreground)]">
            From the blog
          </h2>
          <Link
            href="/blog"
            className="text-xs text-[var(--accent)] hover:underline font-medium"
          >
            View all →
          </Link>
        </div>
        <div className="grid md:grid-cols-3 gap-4">
          {posts.slice(0, 3).map((post) => (
            <Link
              key={post.slug}
              href={`/blog/${post.slug}`}
              className="bg-[var(--card)] border border-[var(--card-border)] rounded-xl p-5 hover:border-[var(--accent)]/40 transition-colors group"
            >
              <div className="flex items-center gap-2 mb-2">
                <time className="text-[10px] text-[var(--muted)]">
                  {post.date}
                </time>
                {post.tags.slice(0, 1).map((tag) => (
                  <span
                    key={tag}
                    className="text-[9px] px-1.5 py-0.5 rounded-full bg-[var(--accent-light)] text-[var(--accent)] font-medium"
                  >
                    {tag}
                  </span>
                ))}
              </div>
              <h3 className="text-sm font-semibold text-[var(--foreground)] group-hover:text-[var(--accent)] transition-colors leading-snug">
                {post.title}
              </h3>
              {post.summary && (
                <p className="text-xs text-[var(--muted)] mt-2 leading-relaxed line-clamp-3">
                  {post.summary}
                </p>
              )}
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="py-10 px-6 border-t border-[var(--card-border)]">
      <div className="max-w-4xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded bg-[var(--accent)] flex items-center justify-center">
            <span className="text-white text-[8px] font-bold">X</span>
          </div>
          <span className="text-xs text-[var(--muted)]">AI Text X-Ray</span>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="/app"
            className="text-xs text-[var(--muted)] hover:text-[var(--foreground)] transition-colors"
          >
            Tools
          </Link>
          <Link
            href="/blog"
            className="text-xs text-[var(--muted)] hover:text-[var(--foreground)] transition-colors"
          >
            Blog
          </Link>
        </div>
      </div>
    </footer>
  );
}

export default function Home() {
  const posts = getAllPosts();

  return (
    <div className="min-h-screen bg-[var(--background)]">
      <NavBar />
      <Hero />
      <ToolCards />
      <HowItWorks />
      <Stats />
      <WhatMakesUsDifferent />
      <BlogPreview posts={posts} />
      <Footer />
    </div>
  );
}
