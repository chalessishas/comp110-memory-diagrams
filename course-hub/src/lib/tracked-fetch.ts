import { trackUsage } from "./usage-tracker";

export async function trackedFetch(url: string, options?: RequestInit): Promise<Response> {
  const res = await fetch(url, options);

  // Read token usage from response headers (set by API routes)
  const inputTokens = parseInt(res.headers.get("x-input-tokens") ?? "0", 10);
  const outputTokens = parseInt(res.headers.get("x-output-tokens") ?? "0", 10);

  if (inputTokens > 0 || outputTokens > 0) {
    trackUsage(inputTokens, outputTokens);
  }

  return res;
}
