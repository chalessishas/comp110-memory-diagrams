# ai-text-detector: Supplement Script Partial-Key Strategy

**Date**: 2026-04-17 09:55
**Trigger**: Research Loop (automated, user not present)
**Context**: Fleet in HOLD ~5h; supplement script (Path C) blocked on 5 API keys

---

## Key Finding: Script Supports Incremental Per-Vendor Execution

`scripts/build_dataset_v6_supplement.py` accepts a `--vendor` flag and runs **one vendor at a time**. The user does NOT need all 5 keys simultaneously:

```bash
python3 scripts/build_dataset_v6_supplement.py --vendor gpt4o-mini --target 24000
python3 scripts/build_dataset_v6_supplement.py --vendor claude-haiku --target 24000
# ... add more vendors as keys become available
python3 scripts/build_dataset_v6_supplement.py --merge  # merge all shards at end
```

Shards are written to `supplement_v6_shards/` and only merged at the final `--merge` step.

---

## 5 Required Keys — Obtainability Assessment

| Key | Provider | Cost Est. (24K samples) | Free Tier? | Notes |
|-----|----------|------------------------|------------|-------|
| `OPENAI_API_KEY` | OpenAI (gpt4o-mini) | ~$10 | No | User very likely has this |
| `ANTHROPIC_API_KEY` | Anthropic (claude-haiku) | ~$48 | No | User almost certainly has this |
| `DASHSCOPE_API_KEY` | Alibaba Cloud (qwen3-max) | ~$2 | Yes — 1M free tokens | Register at dashscope.aliyun.com |
| `ERNIE_API_KEY` | Baidu AI Cloud (ERNIE 5.0) | ~$4 | Yes — free trial | Register at qianfan.baidubce.com |
| `MOONSHOT_API_KEY` | Moonshot AI / Kimi | ~$5 | Yes — ¥15 free credit | Register at platform.moonshot.cn |

**Estimated cost if all 5 run**: ~$70 total across all vendors.

---

## Recommended Action Sequence (when user returns)

1. **Start immediately** with `OPENAI_API_KEY` + `ANTHROPIC_API_KEY` → 48K samples, covers most expensive vendors
2. **Register Alibaba DashScope** (free tier, English UI available) → adds 24K samples at ~$2
3. **Register Baidu Qianfan** → 24K samples at ~$4 (requires Chinese phone number)
4. **Register Moonshot** → 24K samples at ~$5 (simpler registration than Baidu)

Starting with step 1 alone gives 40% of the target corpus. Steps 3-4 require Chinese provider registration which may be a barrier.

---

## Dataset Impact Assessment

Currently dataset_v6 is DeepSeek-heavy (likely ~80%+ of AI samples from DeepSeek). Path C targets:
- 60% DeepSeek + 40% other families after merge
- Cross-family generalization is the core motivation

With only 2/5 vendors (OpenAI + Anthropic), the AI side becomes:
- ~73% DeepSeek + ~27% OpenAI/Anthropic (gpt4o-mini + claude-haiku)
- This is a meaningful improvement but misses Chinese-market LLMs (Qwen, ERNIE, Kimi)

**Recommendation**: Run OpenAI + Anthropic first (2-3 hours), then evaluate whether adding Chinese providers is worth registration friction.

---

## Blocker Resolution

The user's stated blocker was "需要用户提供 5 个 .env.local API keys". This is **partially incorrect** — the user only needs to provide the 2 they likely already have (OPENAI + ANTHROPIC) to start. The other 3 are optional incremental improvements.

This should be surfaced in the next user-facing response.
