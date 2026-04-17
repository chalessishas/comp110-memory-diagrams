# Research Loop 03:06 — Path C Stub Implementation

**Date:** 2026-04-17 03:06:01
**Trigger:** Research Loop (automated, user sleeping)

## Session State Audit

| Project | Status | Blocker |
|---------|--------|---------|
| TOEFL | ✅ Sprint complete | None |
| ai-text-detector | 🟡 Path C skeleton | 5 API keys (user-gated) |
| Signal-Map | 🔴 HOLD | Product direction |
| course-hub | 🔴 HOLD | Architecture decision |

## Work Completed This Loop

Implemented the two TODO stubs in `scripts/build_dataset_v6_supplement.py`:

### 1. `get_client(vendor)` — fully implemented
- Handles `sdk_type="openai"` → `openai.OpenAI(base_url=..., api_key=...)`
- Handles `sdk_type="anthropic"` → `anthropic.Anthropic(api_key=...)`
- Loads `.env.local` via dotenv before checking env vars
- Graceful error on missing import or missing API key

### 2. `generate_sample(vendor, client, topic, style, domain)` — fully implemented
- Signature updated: `prompt` param replaced with `topic + domain` (matches v6 schema)
- Anthropic path: `client.messages.create()` → `response.content[0].text`
- OpenAI path: `client.chat.completions.create()` → `response.choices[0].message.content`
- 3-retry loop with exponential backoff on rate limits
- Chinese-language prompts (5 styles in `AI_PROMPT_STYLES_ZH`)

### 3. `run_vendor()` — full generation loop added
- Resume support: counts existing shard samples + deduplicates by hash
- Topic loading from `dataset_v6.jsonl` human samples, falls back to 12 generic Chinese topics
- Batched periodic flush every 10 samples via open file handle
- Rate limiting: 50ms sleep every 10 samples
- `char_count()` instead of `word_count()` for Chinese text validation

### 4. New: `AI_PROMPT_STYLES_ZH` — Chinese prompts
Five styles in Chinese (standard/formal/casual/academic/creative) matching v6 pattern but
asking for character counts ("约{length}字") rather than word counts.

## Key Design Decisions

**char_count vs word_count:** Chinese text doesn't space-delimit words. `split()` returns ~1
token for most sentences. `char_count()` strips spaces and counts characters — the natural
unit for Chinese.

**Fallback topics:** If `dataset_v6.jsonl` doesn't exist yet, uses 12 hardcoded Chinese
essay topics (education/environment/social media/etc.) so the script can run standalone.

**Signature change:** `generate_sample(vendor, client, prompt, style)` → 
`generate_sample(vendor, client, topic, style, domain)` to match v6 schema which stores domain.

## Verification
- `ast.parse()` → syntax OK
- `--help` → correct output
- `--vendor gpt4o-mini` without API key → `ERROR: OPENAI_API_KEY not set` (correct exit code 1)

## Next Steps for User (when awake)

1. Add 5 API keys to `.env.local`:
   - `OPENAI_API_KEY` (gpt4o-mini)
   - `ANTHROPIC_API_KEY` (claude-haiku) — may already exist
   - `DASHSCOPE_API_KEY` (qwen3-max)
   - `ERNIE_API_KEY` (ernie-5)
   - `MOONSHOT_API_KEY` (kimi-k2.5)

2. Start with cheapest vendor to validate pipeline:
   ```bash
   python3 scripts/build_dataset_v6_supplement.py --vendor qwen3-max --target 100
   ```
   Cost: ~$0.01 for 100 samples. Spot-check 10-20 outputs for quality.

3. If quality OK → run all 5 vendors at full target:
   ```bash
   for vendor in qwen3-max ernie-5 kimi-k2.5 gpt4o-mini claude-haiku; do
       python3 scripts/build_dataset_v6_supplement.py --vendor $vendor --target 24000
   done
   ```

4. Merge + retrain:
   ```bash
   python3 scripts/build_dataset_v6_supplement.py --merge
   # → retrain DeBERTa on merged dataset_v6.jsonl
   ```

## Remaining Risk

`ernie-5` model_id `ernie-speed-128k` and `kimi-k2.5` model_id `moonshot-v1-8k` are
best-guess — verify against vendor documentation before running at scale. Wrong model_id
causes immediate API error, not silent data corruption.
