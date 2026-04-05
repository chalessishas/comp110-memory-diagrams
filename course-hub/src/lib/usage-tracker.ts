const STORAGE_KEY = "coursehub.usage";

export interface UsageRecord {
  date: string;
  inputTokens: number;
  outputTokens: number;
  requests: number;
}

interface UsageStore {
  days: Record<string, UsageRecord>;
}

function todayKey(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function readStore(): UsageStore {
  if (typeof window === "undefined") return { days: {} };
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : { days: {} };
  } catch { return { days: {} }; }
}

function writeStore(store: UsageStore) {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
}

export function trackUsage(inputTokens: number, outputTokens: number) {
  const store = readStore();
  const key = todayKey();
  const day = store.days[key] ?? { date: key, inputTokens: 0, outputTokens: 0, requests: 0 };
  day.inputTokens += inputTokens;
  day.outputTokens += outputTokens;
  day.requests += 1;
  store.days[key] = day;
  writeStore(store);
}

export function getTodayUsage(): UsageRecord {
  const store = readStore();
  return store.days[todayKey()] ?? { date: todayKey(), inputTokens: 0, outputTokens: 0, requests: 0 };
}

export function getWeeklyUsage(): UsageRecord[] {
  const store = readStore();
  const result: UsageRecord[] = [];
  const today = new Date();
  for (let i = 6; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    result.push(store.days[key] ?? { date: key, inputTokens: 0, outputTokens: 0, requests: 0 });
  }
  return result;
}

export function estimateCost(inputTokens: number, outputTokens: number): number {
  // Qwen3.5-Plus pricing: $0.26/M input, $1.56/M output
  return (inputTokens * 0.26 + outputTokens * 1.56) / 1_000_000;
}

export function formatTokens(n: number): string {
  if (n < 1000) return `${n}`;
  if (n < 1_000_000) return `${(n / 1000).toFixed(1)}K`;
  return `${(n / 1_000_000).toFixed(2)}M`;
}
