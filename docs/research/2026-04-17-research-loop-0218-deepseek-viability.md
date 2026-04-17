# Research Loop 02:18 — DeepSeek-focused AI Detector Viability

**时间**：2026-04-17 02:18
**前置**：[Turn 3-6 ai-text-detector dataset_v6 audit](2026-04-17-research-loop-0000-ai-detector-restart.md)
**研究问题**：Turn 4 提出的主人二选一（DeepSeek-only vs general detector）是否还有第三条路？

---

## 1. 2026 市场证据（3 次 WebSearch）

### E1. DeepSeek 中国市场 dominance
- **89% 中国 AI 市场份额**，130M MAU (end 2025), 173M downloads since 2025-01
- 中国 35% / 印度 20% / 印尼 ~5% = 前三大市场占 51% MAUs
- 华为等中国手机默认 chatbot
- URL: https://backlinko.com/deepseek-stats

**对项目**：中文场景 "AI 生成文本" 压倒性来自 DeepSeek；"DeepSeek 检测" 有大市场。

### E2. 腾讯 Zhuque 已做中文 AI 检测
- Tencent 内部工具 Zhuque 检测中英双语 AI 文本，**中文表现被媒体称优异**
- 中国 AI 市场 2025 投资 $125B（政府 $56B）
- Zhipu AI / MiniMax 已香港 IPO（7.1B / ？B 估值）
- URL: https://sourceforge.net/software/ai-content-detection/china/

**对项目**：直接竞品已存在且来自大厂，独立开发者在"通用中文检测"上难赢，必须差异化。

### E3. 多语言检测器中文 accuracy 衰减
- **GPTZero v4.1b 号称 98.79% 24 languages，独立测试中 Arabic/Mandarin 仅 74%**
- Pangram / Copyleaks / Winston AI 都在扩展中文支持
- "Most detectors originally built for English and potentially misjudging work in other languages" — Paper Checker 2026
- URL: https://hub.paper-checker.com/blog/ai-detection-non-english-languages-2026-2/

**对项目**：国际竞品在中文上有 20% accuracy gap → **中文优化**是真实市场机会，但 Pangram 等已在填补，窗口期短。

---

## 2. Turn 4 二选一的扩展

Turn 4 原决策点：
- **路径 A**：DeepSeek-only（按 dataset_v6 现状训）
- **路径 B**：general AI detector（补 GPT/Claude/Gemini/Llama 样本）

新证据下识别**路径 C：中文场景 multi-family, DeepSeek-heavy**：
- 保留 DeepSeek 主导训练（80% AI 样本 = DeepSeek）
- 补 ~120K 样本覆盖中文 GPT-4o/Claude/Qwen-3/ERNIE/Kimi（20% AI 样本）
- **不追 general English detector**（GPTZero/Pangram 有领先）
- **不纯 DeepSeek-only**（Tencent Zhuque 会吃掉这个单家族 niche + 用户在实际场景会混用）

### 路径对比

| 路径 | 训练数据 | 市场定位 | 竞品威胁 | ROI |
|-----|---------|---------|---------|-----|
| A. DeepSeek-only | 700K 现状 | "DeepSeek 检测专家" | **Tencent Zhuque**（大厂资源） | 低（细分太窄） |
| B. General | +400K GPT/Claude/... 均衡 | 通用 AI 检测 | **GPTZero/Pangram**（SOTA 领先 18-24 月） | 低（追赶成本高） |
| **C. 中文 DS-heavy** | 700K + 120K 中文其他家族 | **"中文 AI 检测，DeepSeek 重点"** | 较小（Tencent 通用，GPTZero 中文弱） | **中-高** |

---

## 3. 路径 C 的具体实施

### 3.1 补样本数据（成本估算）
| 模型 | API 成本 | 120K/5 = 24K 样本 × 500 words = 12M tokens | 估 |
|-----|---------|-----|----|
| GPT-4o-mini | $0.15/M in + $0.60/M out | ~$10 | OpenAI |
| Claude Haiku 4.5 | $1/M in + $5/M out | ~$48 | Anthropic |
| Qwen3-Max | ~$0.02/M（国内 API）| ~$2 | 阿里 |
| ERNIE 5.0 | $0.10/M | ~$4 | 百度 |
| Kimi K2.5 | $0.15/M | ~$5 | Moonshot |

**总成本**：~$70 补齐 120K 中文其他家族样本。**相比一次无效 Colab 训练（可能 $5）便宜得多**，且一次投入持续受益。

### 3.2 训练配置调整
- 保留 `train_runpod_v6.py` DANN 架构（domain-adversarial 天然适配多 family）
- 增加 domain label：DeepSeek_clean / DeepSeek_adv / GPT / Claude / Qwen / ERNIE / Kimi
- class_weights 可能要微调——120K 新样本会把 AI 总量推到 420K（60% DeepSeek + 40% 其他）

### 3.3 评估 benchmark
- 必做：每个 family × 100 条 held-out eval，报 per-family F1
- 目标：DeepSeek F1 ≥ 90%（本来就 heavy），其他 family F1 ≥ 80%
- 对标 GPTZero 中文 74% 是 beat 门槛

### 3.4 市场定位
- **不对标 GPTZero/Pangram**（英文 SOTA 不可能追）
- **差异化：中文 AI 检测 + DeepSeek 深度理解**（腾讯 Zhuque 虽然做中文但通用）
- 产品 positioning：**"for Chinese educators / content platforms / HR 应付留学生作业 + 公众号洗稿 + 简历造假的中文 AI 检测"**

---

## 4. 风险 & 不做的事

### 风险
1. **腾讯可能扩 Zhuque 对外开放**：目前主要内部 + 微信生态；一旦对外开放，独立产品空间压缩
2. **DeepSeek 被监管**：89% 份额引发反垄断担忧，如拆分市场变化
3. **中国 AI 检测需求主要来自 B2B**（教育机构、内容平台），不像 GPTZero 那样 to-C 易冲量

### 不做
- **不追英文 SOTA**（GPTZero/Pangram 领先 1.5 年）
- **不做 API detector sold by API**（需 infra，和主人"纯前端"偏好冲突）
- **不碰 Copyleaks/Winston 的中文 coverage**（他们已在填，做 follower 无意义）

---

## 5. 具体 Next Commands（给主人）

如果主人倾向路径 C：

```bash
# 1. 补数据生成（30 分钟本地跑 + API 并发）
cd ai-text-detector
vim scripts/build_dataset_v6_supplement.py  # 新脚本
# 调 5 个中文 API，每个 24K 样本，按 dataset_v6.jsonl 的 domain 分布

# 2. 合并到 dataset_v6.jsonl
python3 scripts/build_dataset_v6_supplement.py --merge

# 3. 重跑本轮 Turn 3 的质量 check
python3 -c "... (Turn 3 Python scan) ..."
# 应看到 source 分布 60% DeepSeek + 40% 其他

# 4. RunPod A100 训练
# 按 train_runpod_v6.py 原 workflow
```

**Gate**：步骤 3 显示比例正确才进步骤 4。$70 数据 + 1-2 小时脚本 vs 3-5 小时 Colab + 无效模型，ROI 明显。

---

## 6. 元观察：Research Loop 的产品价值

Turn 1-6 做了**技术层面的 dataset audit**（数据失衡发现）。本轮做的是**商业定位层面的市场调研**（DeepSeek 89% 市场 + Tencent Zhuque 竞争 + GPTZero 中文 gap）。两者组合给主人一个 **technical × market 的决策矩阵**，不再只是"数据有问题要不要修"的单一维度。

**规律**：ai-text-detector 这类**有市场竞争性的产品项目**，Research Loop 应该同时做 technical audit + market scan；TOEFL 这类 **主人自用工具** 可以只 technical audit。项目性质决定 Research 深度。

---

## Sources

- [DeepSeek AI Usage Stats 2026 — Backlinko](https://backlinko.com/deepseek-stats)
- [DeepSeek Revenue & Usage 2026 — BusinessofApps](https://www.businessofapps.com/data/deepseek-statistics/)
- [Chinese AI Content Detection Tools — SourceForge 2026](https://sourceforge.net/software/ai-content-detection/china/)
- [Top Chinese AI Models 2026 — ZenMux](https://zenmux.ai/blog/top-chinese-ai-models-in-2026-capabilities-use-cases-and-performance)
- [AI Detection Non-English Languages 2026 — Paper Checker](https://hub.paper-checker.com/blog/ai-detection-non-english-languages-2026-2/)
- [GPTZero Multilingual Review 2026](https://gptzero.me/news/what-is-the-best-ai-detector-for-multi-language-detection/)
