# Humanizer 相关论文与技术参考

> 最后更新: 2026-03-22 11:18

---

### StealthRL: Reinforcement Learning for Stealthy Paraphrasing (SOTA)
- **来源**: arXiv Feb 2026 | https://arxiv.org/abs/2602.08934
- **核心发现**: 用 GRPO 对 Qwen3-4B + LoRA rank 32 做 RL 微调，reward = 检测器逃逸分 + 语义相似度。10k 样本 3 epochs。逃逸率 99.9%，AUROC 从 0.74 降到 0.27。攻击可迁移到未见过的检测器
- **对项目的价值**: 终极方案。推理只需单次 forward pass（~2s），比 CoPA 快且效果好 10x。LoRA adapter ~50MB，可在 MLX 加载。Colab A100 训练约 2 小时 ~$5
- **局限性**: 需要云端训练（M4 本地训 10k 样本约 250 小时不现实）。过拟合特定检测器的风险存在，但论文显示迁移性好
- **行动项**: 等 DeBERTa 重训完，用它做 reward detector，在 Colab 训 StealthRL

### CoPA: Contrastive Paraphrase Attacks on LLM-Generated Text Detectors
- **来源**: EMNLP 2025 | https://arxiv.org/abs/2505.15337
- **核心发现**: 用同一个 LLM 的两套 prompt（人类风格 vs 机器风格）做对比解码，公式 `(1+λ)·logits_h - λ·logits_m`，无需训练即可大幅降低检测率。参数 λ=0.5, α=1e-5
- **对项目的价值**: 已实现为 copa_proof.py。四项指标（PPL/ENT/BURST/GLTR）全部进入人类范围。是目前 humanizer 的核心方法
- **局限性**: 论文测试的检测器可能是旧版（2025 年中）。CoPA 没有公开代码，我们的实现是从论文公式复刻的

### DIPPER: A Discourse Paraphraser for Diverse Paraphrasing
- **来源**: NeurIPS 2023 | https://arxiv.org/abs/2303.13408
- **核心发现**: 11B T5 模型专门微调做改写，可控制词汇多样性和语序变化。将 DetectGPT 准确率从 70.3% 降到 4.6%
- **对项目的价值**: 学术 baseline，证明了改写攻击的可行性。但 11B 太大，M4 16GB 跑不了
- **局限性**: 模型太大（11B），且是 2023 年的工作，现代检测器可能已适应

### GradEscape: Gradient-based Attack on AI Text Detectors
- **来源**: USENIX Security 2025
- **核心发现**: 仅用 139M 参数模型，通过梯度优化对抗检测器，效果超过 11B 的 DIPPER。证明模型大小不是关键
- **对项目的价值**: 说明小模型也能做好 humanizer，支持我们用 4B 模型的决策
- **局限性**: 需要白盒访问检测器（知道检测器的梯度），我们的场景是黑盒

### TempParaphraser
- **来源**: EMNLP 2025 | https://aclanthology.org/2025.emnlp-main.1607/
- **核心发现**: 微调 LLM 模拟高温采样效果，逐句改写后用检测器选最佳版本。平均降低检测率 82.5%
- **对项目的价值**: 备选方案。如果 CoPA 不够用，可以考虑这个方向（需要微调）
- **局限性**: 需要微调数据和训练算力

### Adversarial Paraphrasing (NeurIPS 2025)
- **来源**: NeurIPS 2025 | https://arxiv.org/abs/2506.07001
- **核心发现**: 无需训练。用任意指令跟随 LLM 做改写，每步用检测器评分引导解码。87.88% 逃逸率。攻击可跨检测器迁移
- **对项目的价值**: 和 CoPA 互补——CoPA 用双 prompt 对比，这个用检测器评分引导。可以结合使用
- **局限性**: 需要在每个 token 位置调用检测器，非常慢

### Can AI-Generated Text be Reliably Detected? (Sadasivan et al.)
- **来源**: arXiv 2023 | https://arxiv.org/abs/2303.11156
- **核心发现**: 数学证明了对于足够好的语言模型，最优检测器的表现只比随机猜测略好。递归改写可以攻破水印、分类器和零样本检测
- **对项目的价值**: 理论支撑——说明检测问题在根本上是有极限的。我们的产品方向（humanizer）在理论上是可行的
- **局限性**: 理论结果，实际中检测器仍然有用（因为当前 LLM 还没"足够好"到理论极限）

### Uncertainty in Authorship: Why Perfect AI Detection Is Mathematically Impossible
- **来源**: arXiv 2025 | https://arxiv.org/abs/2509.11915
- **核心发现**: 类似量子不确定性——提高检测一个维度的置信度会引入另一个维度的不确定性
- **对项目的价值**: 进一步支持理论可行性
- **局限性**: 和 Sadasivan 一样是理论论文

---

## 检测器侧参考

### Stanford HAI: AI Detectors Biased Against Non-Native English Writers
- **来源**: Stanford HAI 2023 | PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC10382961/
- **核心发现**: 7 个主流 AI 检测器在 TOEFL 作文上 61.3% 误报率（把人类写的判成 AI）。97% 的非母语者文本被至少一个检测器标记
- **对项目的价值**: 产品差异化——我们的检测器应该避免这个偏见。也是 humanizer 的伦理论据（检测器本身不可靠）
- **局限性**: 2023 年数据，检测器可能已改进

### End the AI Detection Arms Race (Patterns 2024)
- **来源**: Patterns | PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC11573885/
- **核心发现**: 学术界的检测军备竞赛不可持续，建议学校改变教学方式而非检测 AI
- **对项目的价值**: 支持产品叙事——我们的 Writing Center 方向（教学而非检测）是学术界推荐的方向
- **局限性**: 立场偏向"停止检测"，可能过于乐观

---

## 水印技术

### Google SynthID
- **来源**: Google DeepMind Blog | https://deepmind.google/blog/watermarking-ai-generated-text-and-video-with-synthid/
- **核心发现**: 在 token 概率分布中嵌入不可感知的统计信号。不影响文本质量。2025 年开源
- **对项目的价值**: 了解竞争格局。水印是检测的替代方案，但需要模型提供商配合
- **局限性**: 改写可以去除水印（arXiv:2508.20228 已证明）

### SynthID Robustness Assessment
- **来源**: arXiv 2025 | https://arxiv.org/abs/2508.20228
- **核心发现**: SynthID 对改写、回译、语法变换脆弱。黑盒查询可以窃取水印模式
- **对项目的价值**: 说明水印不是银弹，改写攻击（我们在做的事）有效
- **局限性**: 测试的是 SynthID 具体实现，其他水印方案可能更鲁棒
