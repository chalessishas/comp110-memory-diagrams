# Vocabulary Notebook Sync Options (Zero-Auth, Cross-Device)

**Date:** 2026-04-12
**Constraint:** ~50 vocabulary words, no user accounts, zero cost, pure frontend preferred

## Key Findings

- **localStorage is strictly same-origin, single-device.** No browser provides native cross-device localStorage sync for arbitrary web apps. Any sync requires either a server or a browser extension.
- **Share-via-URL is the simplest zero-backend option.** Serialize the notebook to JSON, base64-encode it, append to a URL hash (`/notebook#data=...`). Recipient opens the URL and imports. No server, no auth, no infra cost. Works for 50 words easily (base64 of 50 vocab entries ≈ 3-5KB, well under URL length limits).
- **Cloudflare Workers KV free tier** provides 100k reads/day, 1k writes/day, 1GB storage — more than sufficient for vocab sync. A Worker endpoint accepting GET/PUT with a user-supplied UUID as key requires no accounts. However, this requires deploying and maintaining a CF Worker (30-60 min setup), and the free tier limits reset daily — if a user hits 1k writes in a day from heavy use, writes fail silently.
- **PocketBase** is MIT-licensed, single Go binary, runs on any VPS. Real-time subscriptions built-in. But it requires a server (minimum ~$4/month VPS) and is overkill for 50 vocabulary words. Not zero-cost.
- **remoteStorage (FrigadeHQ)** is a hosted localStorage-compatible API with a free tier. Works via same localStorage API. However, without JWT it exposes any key to anyone who knows the endpoint URL — not appropriate for personal vocabulary notebooks.

## Source URLs

- https://github.com/FrigadeHQ/remote-storage
- https://developers.cloudflare.com/kv/platform/pricing/
- https://developers.cloudflare.com/kv/platform/limits/
- https://pocketbase.io/faq/
- https://news.ycombinator.com/item?id=38972358

## Recommendation

**Implement Share-via-URL export/import first — zero infrastructure, ships in 2 hours.**

Specific implementation:
```js
// Export: encode notebook to URL
const data = btoa(JSON.stringify(vocabNotebook))
const url = `${location.origin}/reading#vocab=${data}`
navigator.clipboard.writeText(url)

// Import: parse on page load
const params = new URLSearchParams(location.hash.slice(1))
if (params.has('vocab')) {
  const imported = JSON.parse(atob(params.get('vocab')))
  mergeIntoLocalStorage(imported) // merge, don't overwrite
}
```

If true sync (automatic, no manual export) becomes a priority later, deploy a Cloudflare Worker with a UUID-keyed KV store. Estimated effort: 3-4 hours, zero cost for this use case scale.
