# 2026-04-16 Session 最终总结

**生成时间**：2026-04-16 23:05（opus-0416p，session winding down turn）
**目的**：主人 afk 期间多个 Claude session 并发运行（Research Loop 每小时 + Progress Loop 每 10 分钟 × 多会话），产出极多。本报告是主人回来时的一页纸状态快照，不再按 turn 叙事。

---

## 今日规模

| 维度 | 数量 |
|-----|-----|
| Chronicle turn 条目 | **66** |
| 并发 session | 至少 **2 个 Opus + 2 个 Sonnet**（turn 号冲突印证） |
| TOEFL 项目 commit | **16** |
| Signal-Map 项目 commit | **3** |
| workspace（含 research / chronicle）commit | **30+** |
| Research 报告生成 | **至少 5 份**（见第 4 节） |

---

## 主要产出（按用户可感知度排序）

### 🔴 生产代码改动（真实用户立刻受影响）

1. **Signal-Map normalizer A+B+C**（TOEFL 不受益，Signal-Map 独立）— commit `a0feb5b` → hdmap.live
   - B: substring 匹配对称 min-length guard（阻止 "hall"/"lab" 之类短词误配）
   - C: 多地点字符串 `"Phillips / Sitterson"` 拆分独立 resolve
   - A: `SIGNAL_MAP_LOG_UNMATCHED` flag 门控的 unmatched 日志
   - 预期 74% matchrate → 82-85%（A flag flip 收集一周数据后）

2. **TOEFL Suspense fallback fix**（commit `277bce2`）— lazy route 下载时不再空白屏
   - 影响所有路由：Home / Reading / Writing / BuildSentence / WriteEmail / AcademicDiscussion
   - 改动：1 行，`fallback={null}` → `fallback={<div>Loading…</div>}`

3. **TOEFL WritingResult error display fix**（commit `de5a87d`）— 显示最多 3 个错误 + "+N more"

### 🟡 TOEFL 评分器改进（自用价值，calibration 10/10 维持）

- **Grammar patterns L60-L67**（by multiple sessions）：
  - L60: in-nowadays, be-suppose-to
  - L61: except-of, in-contrary, take-advantage-on
  - L62: be-base-on, worth-of, make-effort-to
  - L63: paragraphStructureBonus（style.js）
  - L64: already/just/yet+past-tense + stative-verb progressive
  - L66: verb+prep collocations（discuss about, emphasize on...）
  - L67A: conjunctive adverb comma-splice（however/therefore/...）

### 🟢 Reading 模块扩充

- **Deep Ocean passage**（`3a01dfe`）— 第 2 篇学术文章，6 种题型
- **Plate Tectonics passage**（`1b97bbb`）— 第 3 篇学术文章 + completion tracking fix
- **text_insertion 题型 × 3**（`e10dfc1`, `eadf9fd`, `ee2cc7f`）— Deep Ocean / Plate Tectonics / Urban Agriculture 各加一题
- **reference 题型**（`146c4cd`）+ 3 篇各补 1 题

### 🔵 新增文件 / 工具

- **TOEFL/tests/scorer-breakdown.js**（诊断脚本）— 每模块 × 权重分解 + S3→S4→S5 gap 分析
- **TOEFL/src/writing/scorer/llmScorer.js**（POC stub）— 本地 MLX 接入，未接聚合
- **docs/fun/WWTI.md** — Wuthering Waves 人格测试 v0.1（30 题 + 10 角色）

---

## 文档债清理

- **TOEFL/CLAUDE.md Pitfall #7**（`731eaf0`）：XSS 从"未做防护"改为"React auto-escape 验证安全 + 未来 Markdown/WYSIWYG 需重审"
- **Signal-Map/CLAUDE.md Haversine**（`5681df6`）：500m 漂移更正为代码实际 100m + 历史脚注
- **Signal-Map/.env.example**（`0f4df67`）：`SIGNAL_MAP_LOG_UNMATCHED` flag 文档化

---

## Research 报告归档

`docs/research/` 今日新增：
1. `2026-04-16-research-loop-1900.md` — LLM rubric scorer（OpenAI API 路径，Turn 17）
2. `2026-04-16-progress-loop-1810-challenge.md` — 规则 scorer HOLD 挑战
3. `2026-04-16-progress-loop-1830-strategic-turn.md` — 规则 scorer 饱和战略转折
4. `2026-04-16-signal-map-normalizer-audit.md` — Signal-Map 建筑匹配率 74% 审计
5. `2026-04-16-research-loop-2036-local-mlx.md` — **本地 MLX 替代方案**（Turn 23，本轮）
6. `2026-04-16-research-loop-1903-writing-feedback-readability.md`（其他 session）
7. `2026-04-16-research-course-hub-*.md`（其他 session）

---

## 等待主人的决策（优先级排序）

### P1 — 激活已就绪的基础设施
- **SIGNAL_MAP_LOG_UNMATCHED=1 on Vercel env**（生产改动，需主人）
  ```bash
  vercel env add SIGNAL_MAP_LOG_UNMATCHED production
  # value: 1
  ```
  开启后一周，从 Vercel logs 提取高频 unmatched locationText 扩 DIRECT_MAPPINGS，匹配率冲 82-85%。

### P2 — 决策 LLM rubric scorer 路径
两份研究报告给了两个路径：
- **路径 A**（Turn 17）：OpenAI API + Vercel Serverless proxy（破坏"纯前端"，$6/月）
- **路径 C**（Turn 23）：本地 MLX `mlx_lm.server`（保留"纯前端"，$0，主人自用场景最优）

推荐 **路径 C**，一键验证：
```bash
/opt/anaconda3/bin/python3.13 -m mlx_lm.server \
  --model mlx-community/Phi-3.5-mini-instruct-4bit \
  --port 8080 --cors-allow "*"
# 然后访问 TOEFL 的 Writing 页面，手动 import llmScorer.js 测几篇，看 QWK 是否比规则器高
```

### P3 — Signal-Map D 改动（Haversine 扩 500m）
等主人说"扩"或"不扩"。Turn 21 已确认 100m 是初始 commit 就有，不是 FP 事故修复，扩到 500m 的风险上限是"回到初始文档意图"。

### P4 — ai-text-detector + chronicle 项目
今日未碰。ai-text-detector 11 天前 commit（v6 training plan + M4 contamination fix），chronicle 5 天前 commit（touch support）。主人回来可评估是否重启其中之一。

---

## 元规律沉淀（今日观察）

1. **LLM agent 代码推理断言的可靠性低**：Turn 12 / 14 / 16 三轮 agent 给的 "X 有 bug Y" 断言都被 2-3 次 Grep/Read 翻转。规则：每个"X 有 bug Y"必须配 Grep 验证 Y 是否真在 X 的代码路径上。
2. **WebSearch 型 agent 更可靠，但有 ~10% 超时率**：Turn 17 / 23 两次 research agent，一次 456s 成功、一次 462s stream idle timeout。fallback = parent 自跑 WebSearch。
3. **规则评分器 S5 天花板饱和 ≠ 算法错**：Turn 15 用 scorer-breakdown.js 实测 S5 已 5/7 模块 = 1.0，这是 TOEFL 0-5 标度内的正常饱和。下一步只能架构升级（LLM）或转向反馈可读性。
4. **生产 env / 支付 / 用户数据 = 主人 gate**：auto loop 可以自由推 local/git，但这三类改动即便 Cron 触发多少次都不跨越（Turn 22 规则）。
5. **Optional-by-default 是最便宜的正反馈架构**：llmScorer.js 独立不接 index.js 聚合，验证后 5-10 行加入、否则静默废弃。
6. **跨项目 audit 是 auto loop 被单项目阻塞后的合理退路**：但仅当 audit 成本 << 实施成本才值得（Turn 19 Signal-Map 审计：Read 194 行 + 写 150 行报告换来 6 个发现 + A+B+C 实施，划算）。
7. **session winding down 的正确姿态**：产出 summary 报告 + 明确待办清单，不撤 Cron（Cron 是主人 gate）。

---

## 推荐主人回来时的 3 步重启流程

1. **（5 分钟）** 扫本报告第 3 节"等待主人的决策"，选一个 P1-P4 执行。
2. **（1 分钟）** 如果选 P2 路径 C：起 `mlx_lm.server`。
3. **（~1 小时）** 随便打几篇 essay 用 llmScorer.js A/B 测，决定是否接入 index.js 聚合权重（Turn 23 建议 10%，从 vocab/org/dev/style 各砍）。

如果都不选，可以关闭 Cron：
```
CronDelete <job_id>  # 具体 ID 通过 CronList 查
```
或者让 7 天自动过期。
