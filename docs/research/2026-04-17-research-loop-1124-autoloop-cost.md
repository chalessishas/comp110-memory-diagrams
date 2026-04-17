# Research Loop 11:24 — Auto-loop 运营成本分析

**时间**：2026-04-17 11:24（session 已跑 ~18h，主人挂机中）
**触发**：双 loop 连续触发后 Turn 20 已写 saturation pointer，避免 duplicate research 转真新方向：**成本分析给主人决策**。

---

## 2026-04 Claude API 价格（WebSearch 确认）

| Model | Input $/M | Output $/M | Cache Hit |
|-------|----------|-----------|-----------|
| Opus 4.7 | $5 | $25 | $0.50 (90% off) |
| Sonnet 4.6 | $3 | $15 | $0.30 |
| Haiku 4.5 | $0.25 | ~$1.25 | $0.025 |
| Batch (any) | 50% off | 50% off | — |

Sources: [Pricepertoken Opus 4.6](https://pricepertoken.com/pricing-page/model/anthropic-claude-opus-4.6), [Finout Anthropic Breakdown](https://www.finout.io/blog/anthropic-api-pricing), [TLDL](https://www.tldl.io/resources/anthropic-api-pricing)

---

## 今日 fleet 真实消耗数据（workspace repo）

- **81 commits** since 2026-04-16 17:00（~18 小时）
- **9 research files** created 2026-04-17
- **77 chronicle turn headers** in 2026-04-17.md（多 session 并发，每 session turn counter 独立）

按 fleet 混合 (Opus + Sonnet) + 每 turn 平均 4-6 次 model call（Read/Grep/Edit/Bash/commit）估算：

| 维度 | 估算 |
|-----|-----|
| 每 turn 输入 token | ~80K (含 CLAUDE.md 25K + chronicle ~20K + file reads ~35K) |
| 每 turn 输出 token | ~3K |
| Opus 每 turn (non-cache) | 80K × $5/M + 3K × $25/M ≈ **$0.48** |
| Opus 每 turn (cache hit 80%) | 64K × $0.50/M + 16K × $5/M + 3K × $25/M ≈ **$0.19** |
| Sonnet 每 turn (cache hit 80%) | 64K × $0.30/M + 16K × $3/M + 3K × $15/M ≈ **$0.11** |

假设 4-6 calls/turn 且 30 turns 总数，fleet 混 50/50：
- Opus 端：30 × 5 × $0.19 = **$28.5**
- Sonnet 端：30 × 5 × $0.11 = **$16.5**
- **18h 总估算：~$45** ≈ **$2.5/hour 或 $60/day**

---

## 主人决策选项

### A. 继续跑（不动 Cron）
成本：~$60/day × 每天 = 月 ~$1,800。对主人的 ROI 取决于产出中 actionable 的部分。今日 81 commits 里实质代码改动（feat/fix）≈ 15-20 个（其余是 chronicle/research docs）。

### B. 降 Cron 频率
把 Progress Loop 从 10min → 30min，Research Loop 保持每 hour，降总触发 3x → 月 ~$600。

### C. 关 Opus 保留 Sonnet
Opus 每 turn 比 Sonnet 贵 1.7x，但 Opus 产出 "代码推理" 类任务（Turn 12 修正 / Turn 15 饱和发现）在 Sonnet 不一定能做好。**不建议关 Opus**，改成 Opus 每 2h 触发一次 Research (深分析)，Sonnet 每 10min 触发 Progress (轻 check)。月 ~$400。

### D. CronDelete 完全
成本 → $0。主人主动触发 session。适合决策 pending 期（现在这样）。

---

## 推荐

**当前状态是 D 最合理**：

1. 昨晚 fleet 已多次 converge 到 "all master-gated" (Turn 11/15/16/17/18/19)
2. 今日新 commit 80% 是 chronicle/research docs，code 改动集中在 TOEFL prose-summary 等小 feature
3. 主人如果离开 > 6h，继续跑 Cron 产出 $ 和 docs 冗余 > 产出 actionable 价值

**主人醒来一键 CronDelete**：
```
CronList  # 查 job ids
CronDelete <research_job_id>
CronDelete <progress_job_id>
```
月 ~$1800 → $0。重新决策 ai-text-detector / TOEFL / chronicle 方向后，手动 `/loop` 再启，**按需跑**。

---

## 元规律

**auto-loop 成本的边际价值曲线**：前 30 min fleet converge 上升（发现 drift / 写 summary），之后长 tail **边际价值趋零**（duplicate short-circuit chronicle）。**sweet spot** 大约是"first 4h then stop"。持续跑超过 4h 只有在有 concurrent master active 时有意义。

主人回来可参考这个数字做 Cron 调度配置。
