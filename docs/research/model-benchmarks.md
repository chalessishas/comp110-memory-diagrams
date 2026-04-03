# 模型评测与价格参考

> 最后更新: 2026-03-22

---

## Humanizer 候选模型（API）

| 模型 | 输入/1M tokens | 输出/1M tokens | 改写 1 篇成本 | SWE-bench | 来源/蒸馏关系 |
|------|---------------|---------------|-------------|-----------|--------------|
| Gemini 2.0 Flash-Lite | $0.075 | $0.30 | ~$0.0002 | — | Google |
| Qwen3.5-Turbo | ~$0.10 | ~$0.50 | ~$0.0003 | — | 阿里，从 Qwen3.5-397B 蒸馏 |
| DeepSeek V3.2 | $0.28 | $0.42 | ~$0.0004 | — | DeepSeek，从自家 R1 蒸馏推理能力。被指控从 Claude 蒸馏 |
| MiniMax M2.7 | $0.30 | $1.20 | ~$0.0007 | 78% | 2026-03-18 发布。被指控从 Claude 蒸馏。自进化训练 |
| Qwen3.5-Plus | $0.26 | $1.56 | ~$0.0009 | — | ≈Qwen3 Max 水平，多模态 |
| Kimi K2.5 | $0.60 | $2.50 | ~$0.0016 | 76.8% | Moonshot，1T MoE/32B 激活，开源。被指控从 Claude 蒸馏 |
| Qwen3 Max | $0.78 | $3.90 | ~$0.002 | — | 阿里旗舰 |

### 蒸馏关系图
```
Claude 4.5/4.6 Opus (Anthropic 指控，2026-02)
    ├─→ DeepSeek (1600 万次查询)
    ├─→ Moonshot/Kimi
    └─→ MiniMax

DeepSeek R1
    └─→ DeepSeek V3/V3.1/V3.2（推理能力蒸馏）

Qwen3.5-397B-A17B
    └─→ Qwen3.5 系列全部小模型（Plus/27B/9B/4B/2B/0.8B）
```

> 注意："蒸馏自 Claude"是 Anthropic 单方面指控，DeepSeek/Moonshot/MiniMax 否认。技术上无法从外部验证。

---

## 本地模型（M4 16GB Mac）

| 模型 | 参数量 | 量化 | 内存占用 | 用途 |
|------|--------|------|---------|------|
| llama3.2:1b | 1B | Q4 | ~1.3GB | perplexity 计算（已部署） |
| qwen3.5:0.8b | 0.8B | Q4 | ~1.0GB | 测试用 |
| qwen3.5-abliterated:2b | 2B | Q4 | ~1.9GB | 去审查版，thinking 好 |
| **qwen3.5:4b (MLX 4-bit)** | 4B | Q4 | ~2.5GB | **CoPA 主力模型** |

---

## Qwen3.5 系列完整对比

| 模型 | 发布日期 | 参数 | AIME 2026 | IFBench | 部署方式 |
|------|---------|------|-----------|---------|---------|
| Qwen3.5-397B-A17B | 2026-02-16 | 397B/17B 激活 | 91.3 | 76.5 | API only |
| Qwen3.5-122B-A10B | 2026-02-24 | 122B/10B 激活 | — | — | 开源 |
| Qwen3.5-35B-A3B | 2026-02-24 | 35B/3B 激活 | — | — | 开源 MoE |
| Qwen3.5-27B | 2026-02-24 | 27B dense | — | — | 开源 |
| Qwen3.5-9B | 2026-03-02 | 9B | 超 GPT-OSS-120B | — | 开源 |
| Qwen3.5-4B | 2026-03-02 | 4B | — | — | 开源，本地可跑 |
| Qwen3.5-2B | 2026-03-02 | 2B | — | — | 开源 |
| Qwen3.5-0.8B | 2026-03-02 | 0.8B | — | — | 开源 |

来源: https://github.com/QwenLM/Qwen3.5, OpenRouter, Alibaba Cloud docs
