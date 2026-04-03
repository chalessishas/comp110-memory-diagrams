# AI 检测相关论文与技术参考

> 最后更新: 2026-03-22 11:18

---

### DivEye: Diversity Boosts AI-Generated Text Detection (IBM)
- **来源**: TMLR 2026 | https://arxiv.org/abs/2509.18880 | https://github.com/IBM/diveye
- **核心发现**: 零样本方法。计算 surprisal 序列的高阶统计量（方差、熵、峰度、偏度）。比所有零样本方法强 33.2%。跨模型泛化好
- **对项目的价值**: 我们已经有 qwen3.5:4b 的 surprisal 数据，只需加 4 个统计特征。预计 LR 从 82% → 88-92%。不需要训练
- **局限性**: 4-bit 量化模型的 surprisal 质量可能低于全精度。需要实测
- **行动项**: clone DivEye repo，提取特征计算逻辑，加入 calibrate_detector.py

### Binoculars: Zero-Shot Detection via Dual LM Contrast (ICML 2024)
- **来源**: ICML 2024 | https://arxiv.org/abs/2401.12070 | https://github.com/ahans30/Binoculars
- **核心发现**: 用两个相似 LM（observer + performer）的交叉熵比值检测。90%+ 检测率 @0.01% FPR。对 ESL 文本 99.67% 准确率（几乎无偏见）
- **对项目的价值**: ESL 友好的零样本信号。可用 llama3.2:1b + qwen3.5:0.8b 实现。适合作为 DeBERTa 的补充
- **局限性**: 需要同时加载两个模型，内存压力。可分阶段加载

---

### TH-Bench: Evaluating Evading Attacks on AI Text Detectors
- **来源**: ACM SIGKDD 2025 | https://arxiv.org/abs/2503.08708
- **核心发现**: 首个综合基准（6 攻击 × 13 检测器 × 6 数据集 × 11 LLM）。发现了"逃检三难"：逃检效果、文本质量、计算成本——三选二
- **对项目的价值**: 直接指导 CoPA 调参——我们选的是"逃检效果 + 文本质量"，牺牲计算成本（best-of-N）
- **局限性**: 2025 年初的检测器版本

### Stylometric Analysis of AI-Generated Texts
- **来源**: Cogent Arts & Humanities 2025 | https://www.tandfonline.com/doi/full/10.1080/23311983.2025.2553162
- **核心发现**: 综合文体特征集（词汇丰富度、句法复杂度、功能词频率、POS bigram）F1=0.94，超过纯 perplexity 方法
- **对项目的价值**: 说明 PPL/ENT 不够——需要文体特征。DeBERTa 隐式学到了这些，但我们的 LR 检测器没有
- **局限性**: 传统 NLP 方法，可能不适合 prompt 工程后的文本

### Why Perplexity and Burstiness Fail to Detect AI (Pangram Labs)
- **来源**: Pangram Blog | https://www.pangram.com/blog/why-perplexity-and-burstiness-fail-to-detect-ai
- **核心发现**: PPL 和 burstiness 作为检测特征已经不够用。现代 AI 文本的 PPL/burstiness 分布和人类重叠严重
- **对项目的价值**: 验证了我们的发现——校准结果显示 PPL 人类 median=16.3，AI median=6.9，确实有重叠。LR 检测器只有 82% 准确率
- **局限性**: Pangram 是竞品，可能有营销动机（推销自己更先进的方法）

### GPTZero Technology (2026 更新)
- **来源**: GPTZero | https://gptzero.me/technology + 竞品对比报告
- **核心发现**: **7 组件管线**（multi-step），99.3% 准确率，0.24% FPR（业界最低）。包含句级分类、上下文感知评分、反改写检测。用深度学习保持与 AI 进化同步
- **对项目的价值**: 7 组件架构 = 多信号 ensemble，验证了我们的方向（DeBERTa + PPL + DivEye）。FPR 0.24% 是我们的目标
- **局限性**: 闭源，具体组件不公开。但 7 组件的思路可以参考

---

### 句级混合检测（未来方向）
- **来源**: EMNLP 2025 | arXiv 2509.17830 + arXiv 2403.03506
- **核心发现**: 两步管线：(1) 分割连续同作者段 (2) 分类每段作者。用 Transformer + CRF 做序列标注。句级 F1 94-99%
- **对项目的价值**: 未来方向。我们的 SentenceAnalysis 组件已做句级评分，可以扩展为句级作者检测。对 Writing Center 特别有价值——帮用户识别哪些句子"太 AI"
- **局限性**: 需要句级标注的训练数据，目前我们没有

---

## 市场数据

### GPTZero 商业数据
- **来源**: Sacra | TechCrunch
- **核心数据**: $24M ARR (2025)，253% YoY 增长，$10M Series A (2024)
- **对项目的价值**: 验证了 AI 检测市场有付费需求

### Turnitin 商业数据
- **来源**: Sacra
- **核心数据**: $203M 收入 (2024)，17,000 机构客户
- **对项目的价值**: 最大的潜在竞争对手，但主要面向机构，不面向个人用户

### DEFACTIFY 4.0: Data Noising for DeBERTa Robustness (1st Place)
- **来源**: arXiv Feb 2025 | https://arxiv.org/abs/2502.16857
- **核心发现**: 在训练数据中注入 10% 随机乱码词（3-8 字符），DeBERTa-v3-small 鲁棒性显著提升。60:40 加权 ensemble（noised 模型 + 顺序微调模型）达到 F1=1.0。关键：noised 数据作为正则化，减少对表层特征的过拟合
- **对项目的价值**: **可立即执行**。我们重训 DeBERTa 时加入 10% 噪声数据增强。不需要额外数据，只需修改训练管线
- **局限性**: DEFACTIFY 数据集可能比真实场景简单。需验证在我们的多文体数据集上效果
- **行动项**: 修改 Colab 训练脚本加入 data noising

### DetectRL: Real-World Scenario Benchmark (NeurIPS 2024)
- **来源**: NeurIPS 2024 D&B | https://arxiv.org/abs/2410.23746 | https://github.com/NLP2CT/DetectRL
- **核心发现**: 覆盖多域、多 LLM、多攻击、变长文本的综合基准。有监督检测器一致优于零样本方法。最佳零样本（Binoculars）只有 79.61%。模拟真实场景：prompt 变体、人工修订、拼写错误、对抗攻击
- **对项目的价值**: 可作为第三个外部数据集补充 RAID + MAGE。真实场景模拟对我们的数据集设计有参考价值
- **局限性**: 数据集文档不完整（HuggingFace 链接待发布）

### Detecting the Machine: Comprehensive Benchmark (2026)
- **来源**: arXiv Mar 2026 | https://arxiv.org/abs/2603.17522
- **核心发现**: 评估多种检测架构在 HC3 + ELI5 上的跨域、跨 LLM 泛化。**关键结论：没有任何方法在跨域迁移时保持鲁棒。** Fine-tuned DeBERTa 在域内近乎完美但域外退化严重
- **对项目的价值**: 直接验证了我们的发现——DeBERTa 98.5% 是域内成绩，跨域（新文体）直接崩溃。必须扩充训练域
- **局限性**: 只用了 HC3 和 ELI5 两个语料库

### SpecDetect: DFT-Based Detection (AAAI 2026 Oral)
- **来源**: AAAI 2026 | https://arxiv.org/abs/2508.11343
- **核心发现**: 将 token log-probability 序列视为信号，用 DFT 频谱分析。人类文本的频谱总能量显著高于 AI 文本。单一特征（DFT total energy）超越 SOTA，速度快一半
- **对项目的价值**: **已实现并验证**。在我们的测试集上 human/AI energy 比 1.33x。作为 ensemble 辅助信号可直接使用
- **局限性**: 分离度在短文本上可能不够。需要和其他信号组合
- **行动项**: 已加入 perplexity.py 的 `compute_specdetect_energy()`

### DetectAnyLLM: Cross-Generator Generalization (2025)
- **来源**: arXiv Sep 2025 | https://arxiv.org/abs/2509.14268
- **核心发现**: Direct Discrepancy Learning (DDL) + LLM-conditional feature alignment 实现跨生成器泛化。构建 MIRAGE 基准（93K 样本，17 LLMs，5 域，10 语料库）。比现有方法提升 70%
- **对项目的价值**: **MIRAGE 数据集**是最有价值的外部数据源——覆盖 17 个现代 LLM（包括 GPT-4、Claude 3.5、Gemini 等），5 个文本域。比 RAID（旧模型为主）更适合我们
- **局限性**: DDL 方法可能需要训练框架修改；MIRAGE 是否完全公开待确认
- **行动项**: 下载 MIRAGE 数据集，提取多域多模型样本合并到训练数据

### AI 检测器准确率独立测试
- **来源**: WalterWrites, Hastewire 等独立评测
- **核心数据**: 尽管声称 95-99%，独立测试中没有一个检测器在混合内容上超过 80% 准确率
- **对项目的价值**: 市场机会——检测器不可靠 = humanizer 有空间

---

## Writing Center 竞品分析

### Khan Academy Writing Coach
- **来源**: https://www.khanmigo.ai/writingcoach
- **核心特点**: 教师监控学生写作过程、防作弊、迭代反馈
- **对项目的价值**: 直接竞品。我们缺教师端功能

### Socrat.ai
- **来源**: https://socrat.ai/
- **核心特点**: 教师定制反馈计划、跨对话记忆、Socratic dialogue
- **对项目的价值**: 记忆功能是差异化方向。我们的 localStorage persistence 是基础版

### Socratic Writing Feedback 研究 (2024-2025)
- **来源**: PMC 2025 研究
- **核心发现**: AI 限制为诊断性评论 + Socratic 提问（禁止生成内容），150-200 词，最多 3 轮。组织和内容发展显著提升
- **对项目的价值**: 我们的 Writing Center guide-dialogue 模式应限制 AI 不直接写内容，只提问引导。当前 prompts 可能需要调整
