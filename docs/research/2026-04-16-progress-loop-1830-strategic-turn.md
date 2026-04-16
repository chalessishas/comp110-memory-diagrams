# Progress Loop 18:30 — 战略转折点

**时间**：2026-04-16 18:30–18:37
**触发**：Progress Loop（用户发送调度消息）
**子 Agent**：ae4c9f23c27306086（general-purpose，第二轮 HOLD 挑战，接力 adbcfcc4a8c5ee35f）
**结论类型**：**项目级战略信号**——不是新增 L64 候选，是"规则评分器已达上限"

---

## 实际状态校验

1. L63（paragraphStructureBonus）已由并行 Sonnet session 实施 —— TOEFL commit `275c45a` @ 18:21:40
2. Calibration 10/10 通过：S1=1.60, S2=2.30/2.70, S3=3.30/2.60, S4=4.30, S5=4.90/4.40
3. 3→4 gap = 1.00（稳定），**4→5 gap = 0.60（未变）**
4. S5 style 从 0.89 → 0.99（接近 1.0 上限），但 style 权重仅 7%，overall 影响 ≈ 0.007，看不出变化

---

## 子 Agent 挑战结论

### 第一轮诊断

对比 S4（120 词单段）vs S5（160 词双段 + 统计数据 + Admittedly 让步）后：
- S4 vs S5 在 organization + development 两模块的**检测命中率差异已低**
- S5 唯一额外优势：
  1. 规范立场句（"organizations should pursue hybrid models..."）
  2. 评价副词 + 名词化密度
  3. Hedging + 数量化数据 co-occurrence

### 第二轮候选方案（agent 自己也不推荐实施）

| 方案 | 位置 | 预期模块增益 | 预期 overall 增益 | 成本 | 风险 |
|---|---|---|---|---|---|
| A. NormativeRecommendation | organization.js L255 附近 | +0.06 | +0.02 | 15 行 | 低 |
| B. EvaluativeAdverbDensity | development.js L296 附近 | +0.08 | +0.01（受 argScore min-gate 限制） | 20 行 | 中（背词模板倒逼） |

**合并预期**：gap 0.60 → 0.56～0.57。硬挤 3 个百分点。

### 关键洞察（agent 自批判里抛出的）

1. **argScore 的 `Math.min(argScore, …)` 是硬 gate**——把它改成 `0.8 * min + 0.2 * sum` 软混合（3 行改动），比做方案 A+B 都管用、成本低 10 倍、且所有现有 bonus 立即生效
2. **产品合理性**：规则评分器刷 0.03 gap 对学生学习价值为零——S4 学生看不出 4.7 和 5 的区别。真正的产品价值在反馈可读性（"你这篇缺规范立场"），不在数字
3. **FP 次生伤害**：方案 B 的评价副词清单一旦上线会倒逼学生背 correctly/deliberately/substantially 当模板词（Granger 1998 "learner chunks" 现象），**反而降低真实 B2+ 学生的分数可信度**

---

## 战略判断

HOLD 的根本原因从"无更多可挑选的 pattern"正式更新为：

> **规则化评分器的 S4→S5 区分力已达架构上限**

继续走 grammar.js / style.js / organization.js / development.js 增量模式匹配，边际收益从 L60 的 +0.03/loop 降到 L64 预测 +0.01/loop，已进入明显递减回报区。

**三个可选路径**：

### 路径 1 — argScore 硬 gate 软化（Quick Win）
- 改 development.js 中 `Math.min(argScore, X)` 为 `0.8 * Math.min + 0.2 * avg`（或类似软混合）
- 成本：3 行
- 预期：所有历史 bonus 累加效应释放，4→5 gap 可能收敛 0.02–0.05
- 风险：中。硬 gate 是设计决定；软化可能让 S3/S4 被推高破坏校准。**必须先读 development.js 完整 argScore 组合逻辑再动手**

### 路径 2 — 架构跃迁：LLM rubric scorer
- 引入小权重（15%）的 LLM-based rubric 评分（Qwen-3.5 / Haiku 4.5 / 本地 MLX）
- 只评"语义质量维"（论证深度、证据-立场连贯性），不评纯语言形式
- 成本：300+ 行（LLM 调用 + prompt 设计 + 缓存 + 回退）
- 预期：4→5 gap 可能收敛到 0.3（架构级改善）
- 风险：高。引入外部依赖、延迟、成本、确定性

### 路径 3 — 承认规则上限，转向反馈可读性
- 接受 gap 0.60 作为规则评分器的设计上限
- 接下来不做评分侧改动，转做 WritingResult.jsx 的"可读诊断"——让学生看到"你缺了什么具体信号"而不是看数字
- 成本：评分侧 0；UI 侧若干
- 预期：对数字 gap 零影响，对学生学习价值最大

---

## 本次 Progress Loop 的决定

**不实施任何代码改动。** 理由：
1. Agent 明确说"停止硬挤规则"
2. Quick Win 路径 1 需要先读 development.js 完整 argScore 逻辑；3 行改动若破坏 10/10 恢复成本高
3. 路径 2/3 都是主人级别的战略决定，不是 auto-loop 能拍板的
4. 主人在场期间不做高风险 ad-hoc 实施

**下次 Research Loop（~19:00）的建议行动**：
- 跑 scorer-calibration.js 并打印每篇样本的 style/organization/development 模块分（当前只打印 overall），量化每模块的 S4→S5 实际 gap，验证 agent 关于 "两模块命中率差异已低" 的断言
- 如果模块分 gap 确实已饱和，把项目正式从"增量 HOLD"切换为"架构决策期"，等主人选路径 1/2/3

---

## 元认知记录

前轮元规则"HOLD > 2h 派子 Agent 挑战"在本次得到验证——前轮挑战出 L63，本轮挑战出"规则已达饱和"。**第二层元规则**：
> 当子 Agent 连续两轮都提出新候选，但这些候选的预期 overall 增益从 0.05 降到 0.01 时，信号不是"继续找第三个候选"，是"整个模式匹配路径已到尽头，需要架构决策"。
