import AppShell from "@/components/AppShell";

export default function Home() {
  return (
    <>
      <AppShell />

      {/* SEO content — visible to crawlers, visually hidden from app users */}
      <div className="sr-only" aria-hidden="false">
        <h1>AI Text X-Ray — Free AI Text Detector & Humanizer</h1>
        <p>
          AI Text X-Ray is a free, explainable AI content detector that goes
          beyond a simple &quot;AI or human&quot; label. It analyzes your text
          using multiple scientific metrics — perplexity, GLTR token ranking,
          entropy, burstiness, and vocabulary diversity — and shows you exactly
          why the text looks AI-generated or human-written.
        </p>
        <h2>Features</h2>
        <ul>
          <li>
            <strong>AI Detector</strong> — Paste any text and get a detailed
            breakdown of perplexity scores, GLTR token rank distribution,
            entropy patterns, sentence burstiness, and a sliding-window analysis.
          </li>
          <li>
            <strong>AI Humanizer</strong> — Transform AI-generated text to read
            more naturally using corpus-based sentence matching, phrase swapping,
            collocation replacement, and noise injection.
          </li>
          <li>
            <strong>Writing Center</strong> — Generate optimized prompts for
            ChatGPT and Claude that produce text matching natural human writing
            patterns, making humanization more effective.
          </li>
        </ul>
        <h2>How It Works</h2>
        <p>
          Our detector computes token-level log-probabilities using a language
          model, then derives features like perplexity (how surprised the model
          is by the text), GLTR rank distribution (how often the model&apos;s top
          predictions match the actual tokens), entropy (uncertainty at each
          position), and burstiness (variation in sentence length and
          complexity). AI-generated text tends to have low perplexity, high
          top-10 token ratios, and low burstiness compared to human writing.
        </p>
        <h2>Free AI Text Detection</h2>
        <p>
          Unlike other AI detectors, AI Text X-Ray is completely free, shows its
          work with interactive charts, and provides sentence-level scoring so
          you can see which parts of your text look most AI-generated.
        </p>
      </div>
    </>
  );
}
