// In production (Vercel), uses Upstash Redis for distributed rate limiting.
// Locally (no env vars set), falls back to in-memory map.

import type { Ratelimit as RatelimitType } from "@upstash/ratelimit";

let redis: import("@upstash/redis").Redis | null = null;
const limiterCache = new Map<string, RatelimitType>();

function getRedis() {
  if (redis) return redis;
  const url = process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.UPSTASH_REDIS_REST_TOKEN;
  if (!url || !token) return null;
  const { Redis } = require("@upstash/redis");
  redis = new Redis({ url, token });
  return redis;
}

function getUpstashLimiter(maxRequests: number, windowMs: number): RatelimitType | null {
  const r = getRedis();
  if (!r) return null;

  const cacheKey = `${maxRequests}:${windowMs}`;
  if (limiterCache.has(cacheKey)) return limiterCache.get(cacheKey)!;

  const { Ratelimit } = require("@upstash/ratelimit");
  const windowSec = Math.ceil(windowMs / 1000);
  const limiter: RatelimitType = new Ratelimit({
    redis: r,
    limiter: Ratelimit.slidingWindow(maxRequests, `${windowSec} s`),
    analytics: true,
    prefix: "coursehub",
  });
  limiterCache.set(cacheKey, limiter);
  return limiter;
}

// Fallback: in-memory (works locally, broken in multi-instance prod)
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
  const limiter = getUpstashLimiter(maxRequests, windowMs);
  if (!limiter) return inMemoryCheck(key, maxRequests, windowMs);

  const { success } = await limiter.limit(key);
  return success;
}
