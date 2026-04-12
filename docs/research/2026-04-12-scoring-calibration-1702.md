# TOEFL 评分权重校准研究

> Research Loop 自动触发 — 2026-04-12 17:02

## 背景

App 评分引擎权重为手动调整，未与真实 e-rater 输出做基准验证（TOEFL/CLAUDE.md Known Pitfall #8）。本报告基于 ETS 公开技术报告和学术文献对现有权重提出校准建议。

---

## e-rater 与人工评分的相关性

ETS 公开标准：**QWK ≥ 0.70，Pearson r ≥ 0.70**（e-rater vs 人工评分）。

关键历史发现：
- e-rater v99（早期）仅比纯字数多解释 0.05 方差；v2.0+ 提升至 0.14
- 启示：**单纯字数与分数相关 r = 0.50–0.70**，是最强单一预测变量
- 纯启发式系统（如本 App）预期 r ≈ 0.50–0.65

---

## e-rater 已知局限（用户须知）

1. **Length inflation** — 字数膨胀会拉高自动评分，但人工评分不接受这种作弊
2. **Content blindness** — 无法检测跑题（无主题专项词汇模型）
3. **无论证质量** — 创意/论点好坏对自动评分不可见
4. **方言偏差** — e-rater 对 AAVE 方言评分低于人工评分（dialect bias）

**建议在 App 结果页加一行 disclaimer**：
> "This score reflects surface features only and cannot assess argument quality, accuracy, or originality."

---

## 可用于校准的开源数据集

| 数据集 | 规模 | 分数标注 | 链接 |
|--------|------|----------|------|
| ASAP/Hewlett (Kaggle 2012) | ~12,000 篇 | 专家双评 | kaggle.com/c/asap-aes |
| TOEFL11 Corpus (LDC) | 1,100 篇 | 无分数（仅母语标注） | ldc.upenn.edu |
| ETS 私有语料 | N/A | 需机构协议 | — |

> Set 1/2 of ASAP 是论证类文章，最接近 TOEFL Independent 任务。

---

## 分数分布参考（ETS 2023）

- 量表：0–5（0.5 档），转换 0–30 section score
- **全球考生均值：约 3.5–3.6 / 5**
- 典型分布集中在 3.0–4.0；5 分约占前 10%；1–2 分较罕见
- Integrated 任务比 Independent 平均低 0.2–0.3 分

⚠️ **App 当前风险**：若普通作答得 4.0+ 则评分过于宽松，会损害用户信任和诊断价值。**目标：普通作答应落在 3.0–3.5**。

---

## 各维度预测力（r 与人工评分）

| 特征 | r 估计 |
|------|--------|
| 字数/篇幅 | 0.50–0.70（最强） |
| 语篇连接词/衔接 | 0.45–0.60 |
| 词汇复杂度（稀有词、AWL） | 0.40–0.55 |
| 语法/机械错误率 | 0.40–0.50 |
| 句式多样性 | 0.30–0.45 |
| TTR | 0.25–0.35（最弱，可被刷） |

ETS 因子分析（Chen 2017）确认三因子结构：**Discourse、Grammar、Word Usage** — 与 App 架构吻合。

---

## 权重调整建议

| 维度 | e-rater (2010) | App 当前 | 建议 |
|------|---------------|---------|------|
| Organization | 32% | 30% | **保持 30%** |
| Development | 29% | 24% | **提升至 28–29%** |
| Vocabulary | ~14% | 18% | **降至 14%** |
| Mechanics | 10% | 10% | 保持 |
| Grammar | 7% | 7% | 保持 |
| Style | 3% | 3% | 保持 |
| Relevance | ~3% | 8% | **降至 4–5%** |

> **最大风险**：Relevance 8% 若仅基于 naive keyword overlap，会因关键词复读而高估分数。优先降权。

---

## 最高 ROI 补充特征

**学术搭配/习语模式（Academic collocation patterns）**：
- e-rater v8 将其作为独立正向特征
- 最能区分 4 分和 5 分的单一指标
- 实现方案：~200 AWL 固定搭配词表查找（约 30 行 JS，零依赖）
- 示例搭配：*significant impact on / contribute to / in contrast to / as a result of*

---

## 实施优先级

1. **降 Relevance 至 4–5%**（10 分钟，高置信度）
2. **提升 Development 至 28–29%，降 Vocabulary 至 14%**（10 分钟）
3. **添加结果页 disclaimer**（5 分钟）
4. **AWL 搭配特征**（1–2 小时，高区分度）
5. **用 ASAP 数据集做 spot-check 验证**（半天，需用户决策）

---

*来源：ETS RR-04-04, Attali & Burstein (2006), Attali/Bridgeman/Trapani (2010), Chen (2017), ETS Score Interpretive Guide 2023*
