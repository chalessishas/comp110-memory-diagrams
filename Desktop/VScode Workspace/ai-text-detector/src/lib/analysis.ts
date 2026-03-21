export interface TokenData {
  token: string;
  logprob: number;
  perplexity: number;
  rank: number;
  entropy: number;
  position: number;
}

export interface SentenceData {
  index: number;
  text: string;
  wordCount: number;
  avgWordLength: number;
}

export interface SlidingWindowData {
  position: number;
  score: number;
  label: string;
}

export interface GLTRData {
  top10: number;
  top100: number;
  top1000: number;
  above1000: number;
}

export interface EntropyData {
  mean: number;
  std: number;
}

export interface VocabData {
  ttr: number;
  hapaxRatio: number;
  uniqueWords: number;
  totalWords: number;
}

export interface BurstinessData {
  lengthCV: number;
  complexityCV: number;
}

export interface SentenceLengthData {
  mean: number;
  std: number;
  histogram: { length: number; count: number }[];
}

export interface SentenceScoreData {
  index: number;
  text: string;
  wordCount: number;
  aiScore: number;
  perplexity: number;
  label: string;
}

export interface FeatureScore {
  name: string;
  score: number;
  weight: number;
  raw: number;
  humanRef: string;
  aiRef: string;
}

export interface ClassificationResult {
  label: number;
  label_name: string;
  probabilities: Record<string, number>;
  ai_score: number;
}

export interface AnalysisResult {
  tokens: TokenData[];
  sentences: SentenceData[];
  slidingWindow: SlidingWindowData[];
  gltr: GLTRData;
  entropy: EntropyData;
  vocabulary: VocabData;
  burstiness: BurstinessData;
  sentenceLength: SentenceLengthData;
  overallPerplexity: number;
  overallScore: number;
  featureScores: FeatureScore[];
  sentenceScores: SentenceScoreData[];
  wordCount: number;
  scoringEligible: boolean;
  classification?: ClassificationResult;
}

// --- Processing ---

export function processTokens(
  raw: { token: string; logprob: number; rank: number; entropy: number }[]
): TokenData[] {
  return raw.map((t, i) => ({
    token: t.token,
    logprob: t.logprob,
    perplexity: Math.exp(-t.logprob),
    rank: t.rank,
    entropy: t.entropy,
    position: i,
  }));
}

// --- Feature computation ---

export function computeGLTR(tokens: TokenData[]): GLTRData {
  if (tokens.length === 0)
    return { top10: 0, top100: 0, top1000: 0, above1000: 0 };

  let t10 = 0,
    t100 = 0,
    t1000 = 0,
    above = 0;
  for (const t of tokens) {
    if (t.rank <= 10) t10++;
    else if (t.rank <= 100) t100++;
    else if (t.rank <= 1000) t1000++;
    else above++;
  }
  const n = tokens.length;
  return {
    top10: (t10 / n) * 100,
    top100: (t100 / n) * 100,
    top1000: (t1000 / n) * 100,
    above1000: (above / n) * 100,
  };
}

export function computeEntropyStats(tokens: TokenData[]): EntropyData {
  if (tokens.length === 0) return { mean: 0, std: 0 };
  const vals = tokens.map((t) => t.entropy);
  const mean = vals.reduce((a, b) => a + b, 0) / vals.length;
  const variance =
    vals.reduce((sum, v) => sum + (v - mean) ** 2, 0) / vals.length;
  return { mean, std: Math.sqrt(variance) };
}

export function computeVocabulary(text: string): VocabData {
  const words = text
    .split(/\s+/)
    .map((w) => w.toLowerCase().replace(/[^\p{L}\p{N}']/gu, ""))
    .filter((w) => w.length > 0);
  const freq: Record<string, number> = {};
  for (const w of words) freq[w] = (freq[w] || 0) + 1;
  const uniqueWords = Object.keys(freq).length;
  const hapax = Object.values(freq).filter((c) => c === 1).length;
  return {
    ttr: words.length > 0 ? uniqueWords / words.length : 0,
    hapaxRatio: words.length > 0 ? hapax / words.length : 0,
    uniqueWords,
    totalWords: words.length,
  };
}

function avgWordLen(text: string): number {
  const words = text.split(/\s+/).filter((w) => w.length > 0);
  if (words.length === 0) return 0;
  return (
    words.reduce((sum, w) => sum + w.replace(/[^a-z]/gi, "").length, 0) /
    words.length
  );
}

export function computeSentences(text: string): SentenceData[] {
  const sentenceRegex = /[^.!?。！？\n]+[.!?。！？]*/g;
  const matches = text.match(sentenceRegex);
  let segments = matches
    ? matches.map((s) => s.trim()).filter((s) => s.length > 0)
    : text
        .split(/\n+/)
        .map((s) => s.trim())
        .filter((s) => s.length > 0);

  if (segments.length === 0) segments = [text.trim()];

  return segments.map((s, i) => ({
    index: i,
    text: s,
    wordCount: s.split(/\s+/).filter((w) => w.length > 0).length,
    avgWordLength: avgWordLen(s),
  }));
}

export function computeSentenceLengthStats(
  sentences: SentenceData[]
): SentenceLengthData {
  if (sentences.length === 0) return { mean: 0, std: 0, histogram: [] };
  const lengths = sentences.map((s) => s.wordCount);
  const mean = lengths.reduce((a, b) => a + b, 0) / lengths.length;
  const variance =
    lengths.reduce((sum, l) => sum + (l - mean) ** 2, 0) / lengths.length;
  const freqMap: Record<number, number> = {};
  for (const l of lengths) freqMap[l] = (freqMap[l] || 0) + 1;
  return {
    mean,
    std: Math.sqrt(variance),
    histogram: Object.entries(freqMap)
      .map(([k, v]) => ({ length: Number(k), count: v }))
      .sort((a, b) => a.length - b.length),
  };
}

export function computeBurstiness(sentences: SentenceData[]): BurstinessData {
  if (sentences.length < 2) return { lengthCV: 0, complexityCV: 0 };
  const lengths = sentences.map((s) => s.wordCount);
  const meanL = lengths.reduce((a, b) => a + b, 0) / lengths.length;
  const stdL = Math.sqrt(
    lengths.reduce((s, l) => s + (l - meanL) ** 2, 0) / lengths.length
  );
  const cx = sentences.map((s) => s.avgWordLength);
  const meanC = cx.reduce((a, b) => a + b, 0) / cx.length;
  const stdC = Math.sqrt(
    cx.reduce((s, c) => s + (c - meanC) ** 2, 0) / cx.length
  );
  return {
    lengthCV: meanL > 0 ? stdL / meanL : 0,
    complexityCV: meanC > 0 ? stdC / meanC : 0,
  };
}

// --- Sliding window (perplexity-based, for visualization) ---

function perplexityToAiScore(ppl: number): number {
  const logPpl = Math.log(Math.max(1, ppl));
  const score = 120 - 30 * logPpl;
  return Math.min(100, Math.max(0, score));
}

export function computeSlidingWindow(
  tokens: TokenData[],
  windowSize = 20,
  step = 5
): SlidingWindowData[] {
  const results: SlidingWindowData[] = [];
  if (tokens.length === 0) return results;

  if (tokens.length < windowSize) {
    const avgLogprob =
      tokens.reduce((sum, t) => sum + t.logprob, 0) / tokens.length;
    results.push({
      position: 0,
      score: perplexityToAiScore(Math.exp(-avgLogprob)),
      label: tokens.map((t) => t.token).join(""),
    });
    return results;
  }

  for (let i = 0; i <= tokens.length - windowSize; i += step) {
    const win = tokens.slice(i, i + windowSize);
    const avgLogprob =
      win.reduce((sum, t) => sum + t.logprob, 0) / win.length;
    const label = win
      .slice(0, 5)
      .map((t) => t.token)
      .join("")
      .trim();
    results.push({
      position: i,
      score: perplexityToAiScore(Math.exp(-avgLogprob)),
      label: label + "...",
    });
  }
  return results;
}

// --- Overall perplexity ---

export function computeOverallPerplexity(
  tokens: TokenData[]
): { perplexity: number } {
  if (tokens.length === 0) return { perplexity: 0 };
  const avgLogprob =
    tokens.reduce((sum, t) => sum + t.logprob, 0) / tokens.length;
  return { perplexity: Math.exp(-avgLogprob) };
}

// --- Per-sentence scoring ---

export function computeSentenceScores(
  sentences: SentenceData[],
  tokens: TokenData[]
): SentenceScoreData[] {
  if (tokens.length === 0 || sentences.length === 0) return [];

  const totalWords = sentences.reduce((s, sent) => s + sent.wordCount, 0);
  if (totalWords === 0) return [];

  const result: SentenceScoreData[] = [];
  let tIdx = 0;

  for (let i = 0; i < sentences.length; i++) {
    const sent = sentences[i];
    const isLast = i === sentences.length - 1;
    const count = isLast
      ? tokens.length - tIdx
      : Math.max(1, Math.round((sent.wordCount / totalWords) * tokens.length));
    const sentTokens = tokens.slice(tIdx, tIdx + count);
    tIdx += count;

    if (sentTokens.length === 0) {
      result.push({
        index: sent.index,
        text: sent.text,
        wordCount: sent.wordCount,
        aiScore: 50,
        perplexity: 0,
        label: "Mixed",
      });
      continue;
    }

    const avgLogprob =
      sentTokens.reduce((s, t) => s + t.logprob, 0) / sentTokens.length;
    const ppl = Math.exp(-avgLogprob);
    const aiScore = perplexityToAiScore(ppl);
    const label =
      aiScore > 70 ? "AI-like" : aiScore > 30 ? "Mixed" : "Human-like";

    result.push({
      index: sent.index,
      text: sent.text,
      wordCount: sent.wordCount,
      aiScore,
      perplexity: ppl,
      label,
    });
  }

  return result;
}

// --- Multi-feature scoring ---

function clamp(v: number, lo: number, hi: number): number {
  return Math.min(hi, Math.max(lo, v));
}

export function computeFeatureScores(
  ppl: number,
  gltr: GLTRData,
  entropy: EntropyData,
  burstiness: BurstinessData,
  vocabulary: VocabData
): { featureScores: FeatureScore[]; overallScore: number } {
  const features: FeatureScore[] = [
    {
      name: "Perplexity",
      score: 1 - clamp((Math.log(Math.max(1, ppl)) - 1.0) / 2.7, 0, 1),
      weight: 0.3,
      raw: ppl,
      humanRef: "20-50",
      aiRef: "3-8",
    },
    {
      name: "Token Rank (GLTR)",
      score: clamp((gltr.top10 - 60) / 35, 0, 1),
      weight: 0.25,
      raw: gltr.top10,
      humanRef: "<75% top-10",
      aiRef: ">90% top-10",
    },
    {
      name: "Entropy",
      score: 1 - clamp((entropy.mean - 1.0) / 2.5, 0, 1),
      weight: 0.25,
      raw: entropy.mean,
      humanRef: "2.5-3.5",
      aiRef: "1.0-2.0",
    },
    {
      name: "Burstiness",
      score: 1 - clamp((burstiness.lengthCV - 0.1) / 0.5, 0, 1),
      weight: 0.15,
      raw: burstiness.lengthCV,
      humanRef: "0.35-0.65",
      aiRef: "0.10-0.20",
    },
    {
      name: "Vocabulary",
      score: 1 - clamp((vocabulary.ttr - 0.5) / 0.4, 0, 1),
      weight: 0.05,
      raw: vocabulary.ttr,
      humanRef: "0.75-0.90",
      aiRef: "0.65-0.80",
    },
  ];

  const overallScore =
    features.reduce((sum, f) => sum + f.score * f.weight, 0) * 100;
  return { featureScores: features, overallScore };
}
