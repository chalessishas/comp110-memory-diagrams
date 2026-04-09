// In production (Vercel), uses Upstash Redis for distributed rate limiting.
// Locally (no env vars), falls back to in-memory map.

let ratelimit: import("@upstash/ratelimit").Ratelimit | null = null;

function getUpstashLimiter() {
  if (ratelimit !== null) return ratelimit;
  const url = process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.UPSTASH_REDIS_REST_TOKEN;
  if (!url || !token) return null;

  // Lazy import to avoid errors when packages aren't installed
  const { Ratelimit } = require("@upstash/ratelimit");
  const { Redis } = require("@upstash/redis");
  const redis = new Redis({ url, token });
  ratelimit = new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(10, "60 s"),
    analytics: true,
    prefix: "coursehub",
  });
  return ratelimit;
}

// Fallback: in-memory (works locally, not suitable for multi-instance prod)
const fallbackMap = new Map<string, { count: number; resetAt: number }>();

function inMemoryCheck(key: string, maxRequests: number, windowMs: number): boolean {
  const now = Date.now();
  const record = fallbackMap.get(key);
  if (!record || now > record.resetAt) {
    fallbackMap.set(key, { count: 1, resetAt: now + windowMs });
    return true;
  }
  if (record.count >= maxRequests) return false;
  record.count++;
  return true;
}

export async function checkRateLimit(
  key: string,
  maxRequests: number = 5,
  windowMs: number = 60_000,
): Promise<boolean> {
  const limiter = getUpstashLimiter();
  if (!limiter) return inMemoryCheck(key, maxRequests, windowMs);

  const { success } = await limiter.limit(key);
  return success;
}
