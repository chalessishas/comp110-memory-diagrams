# AI 文本检测系统改善方案：基于最新论文的研究报告

> 日期: 2026-03-25
> 约束: CPU-only (Railway), $20/月, DeBERTa-v3-base 架构, DeepSeek API $0.14/M tokens

---

## 一、问题诊断：为什么 eval 98.7% 但红队只有 50%

### 根因分析

| 现象 | 根因 | 论文佐证 |
|------|------|----------|
| v3 eval 98.7% 但红队 AI 检测仅 33% | **分布偏移**：83K 训练数据 98% 是 essay，红队用了创意写作/法律/代码评审 | "Detecting the Machine" (arXiv 2603.17522, Mar 2026): "no method generalizes robustly across domains...DeBERTa-v3 is competitive in-distribution but severely miscalibrated cross-domain" |
| v3 对抗防御崩溃 (33%) | **过拟合表层特征**：83K 大数据集让模型学到了 essay 的文体模式而非 AI 的本质特征 | Confounding Neurons (Borile & Abrate, EMNLP Findings 2025): "linguistic and domain confounders introduce spurious correlations, leading to poor OOD performance" |
| v1 vs v3 互补 | v1 数据少但跨域信号保留更好；v3 数据多但 essay 偏见更重 | DivEye (Basani & Chen, TMLR 2026): "human text exhibits richer variability in lexical and structural unpredictability — a global signature robust to domain shifts" |

### 核心结论

**问题不在模型架构，而在训练数据分布和信号组合方式。** 当前系统的 86% 理论上限（oracle routing analysis）和 50% 实际表现之间的 gap，主要来自：
1. 跨域数据严重不足（200 条 vs 83K）
2. 单一 DeBERTa 没有互补信号兜底
3. 没有针对域的路由/阈值适配

---

## 二、方案矩阵

按 **可行性（CPU-only + $20/月）** 和 **预期收益** 排序：

### 方案 A：Confounding Neuron Suppression（零成本，立即可做）

**论文**: Borile & Abrate, "How to Generalize the Detection of AI-Generated Text: Confounding Neurons", EMNLP Findings 2025
- https://aclanthology.org/2025.findings-emnlp.1388/

**方法**: 识别并抑制 DeBERTa feed-forward MLP 中编码了数据集偏见（而非任务信号）的神经元。post-hoc 干预，不需要重训练。

**关键数字**:
- 移除仅 20 个神经元（~0.05% of params）→ OOD 提升 **+6.9%**
- 同时改善 in-domain 和 out-of-distribution 表现

**成本**: $0。纯推理时干预，修改 forward pass 即可。
**可行性**: 极高。只需要一小批跨域标注数据（~100 条）来识别 confounding neurons。
**预期提升**: v1 从 72% → ~77%，v3 从 50% → ~55%。单独效果有限但零成本。

**实施步骤**:
1. 准备 100 条跨域标注样本（法律、创意写作、代码评审、学术论文）
2. 逐层分析 DeBERTa MLP 中间层的神经元激活
3. 用交叉验证识别 topic-specific neurons
4. 在推理时 zero-out 这些神经元

---

### 方案 B：v1/v3 Ensemble + Genre Router（低成本，1-2 周）

**论文**:
- MoSEs (Wu et al., EMNLP 2025): "Mixture of Stylistic Experts with Conditional Thresholds"
  - https://aclanthology.org/2025.emnlp-main.294/
  - **+11.3%** standard, **+39.2%** low-resource
- DoGEN (Tripathi et al., 2025): "Domain Gating Ensemble Networks"
  - https://arxiv.org/abs/2505.13855
  - **95.8% AUROC** out-of-domain, outperforms 32B single model

**方法**: 用 TF-IDF+LR 做 genre router，根据文本类型路由到 v1 或 v3，并用 Platt scaling 校准置信度。

**为什么这是最优先方案**:
- v1 强项：对抗防御 100%，AI 检测 50%
- v3 强项：Human 识别 83%（低 false positive）
- 互补性极强：v1 抓对抗/AI，v3 减误判

**架构**:
```
Text → TF-IDF Genre Router (essay/creative/professional/adversarial)
         ├── essay/academic  → v3 (strong at human recognition)
         ├── creative/mixed  → weighted blend (0.4*v1 + 0.6*v3)
         ├── professional    → v1 (better cross-domain)
         ├── adversarial     → v1 (100% defense rate)
         └── confidence < 0.7 → both models, take higher ai_score
```

**成本**: $0 额外。v1 和 v3 权重都已有，TF-IDF+LR 是 scikit-learn。
**内存影响**: 同时加载两个 DeBERTa = ~1.5GB RAM（Railway 容量内）。
**预期提升**: 55% → **72-78%**（基于 MoSEs 的 +11-39% 改善幅度）。

**Platt Scaling 细节**:
- 用 500+ 跨域标注样本做 calibration set
- 对 v1 和 v3 分别拟合 sigmoid 校准函数
- 校准后的概率更可靠，减少过自信误判

---

### 方案 C：PIFE — 对抗攻击量化检测（中等成本，2-3 周）

**论文**: "Modeling the Attack: Detecting AI-Generated Text by Quantifying Adversarial Perturbations"
- arXiv 2510.02319 (Sep 2025)
- https://arxiv.org/abs/2510.02319

**方法**: PIFE (Perturbation-Invariant Feature Engineering) — 将输入文本通过多阶段标准化管线，然后量化原文与标准化文本之间的差异（Levenshtein distance + 语义相似度），将这些 delta 作为额外特征。

**关键数字**:
- 常规对抗训练在语义攻击下 TPR@1%FPR = **48.8%**
- PIFE 在同等条件下 TPR@1%FPR = **82.6%**（+33.8pp）
- 专门针对"加错别字、注入俚语"等你的红队攻击类型

**为什么这个方案匹配你的问题**:
- v1 对抗防御 100% 但 v3 崩溃到 33% → PIFE 可以补救 v3 的对抗弱点
- PIFE 的标准化管线（拼写纠正、去俚语、重新格式化）和你的红队攻击（加错别字、注入俚语）完全对口

**成本**: $0-2/月（标准化管线用 spaCy + hunspell，已有依赖）。
**CPU 可行性**: 完全 CPU 可行，标准化管线是纯 NLP 处理。
**预期提升**: 对抗场景从 33% → **65-75%**。

**实施步骤**:
1. 建立文本标准化管线：拼写纠正 → 去俚语 → 重新断句
2. 计算 Levenshtein distance（字符级/词级）
3. 计算语义相似度（用已有的 SentenceTransformer）
4. 将这些 delta 特征拼入 DeBERTa softmax 输出，用 LR 做最终决策

---

### 方案 D：DeTeCtive 的 TFIA 机制（中等成本，2 周）

**论文**: He et al., "DeTeCtive: Detecting AI-generated Text via Multi-Level Contrastive Learning", NeurIPS 2024
- https://arxiv.org/abs/2410.20964
- https://github.com/heyongxin233/DeTeCtive

**方法**: Training-Free Incremental Adaptation (TFIA) — 用多层对比学习训练特征提取器，推理时通过 KNN 匹配特征库做分类。关键创新：**添加新域数据不需要重训模型**，只需往特征库里加样本。

**关键数字**:
- 跨域跨模型：超过第二名 **6.52%** (M4-monolingual) 和 **7.15%** (M4-multilingual)
- OOD unseen domains: TFIA 额外提升 **+7.03%**
- OOD unseen models: 额外提升 **+0.84%**

**为什么匹配你的问题**:
- 你的跨域数据只有 200 条 → TFIA 不需要重训，直接把新域样本加入特征库
- 每次发现新的失败域，几分钟内就能"修复"

**成本**: 初始训练需要 GPU（Colab T4 ~2-3小时），之后推理纯 CPU。
**CPU 可行性**: KNN 推理完全 CPU 可行（FAISS 你已经有了）。
**预期提升**: 跨域场景 +7%。

**权衡**: 需要替换或补充 DeBERTa 的特征提取方式，架构改动较大。

---

### 方案 E：DP-Net — 动态扰动增强泛化（中等成本，需 GPU 训练）

**论文**: Zhou et al., "Kill two birds with one stone: generalized and robust AI-generated text detection via dynamic perturbations", NAACL 2025
- https://aclanthology.org/2025.naacl-long.446/

**方法**: 在 DeBERTa embedding 层加入 RL 生成的动态扰动噪声，模拟域偏移和对抗攻击，让模型同时获得泛化性和鲁棒性。

**关键数字**:
- **3 个跨域场景 SOTA**
- **2 种对抗攻击下最佳鲁棒性**
- 同时解决泛化和鲁棒——正好是你 v3 的两个弱点

**成本**: Colab T4 训练 ~3-5 小时。推理时无额外成本。
**CPU 可行性**: 训练完后推理和普通 DeBERTa 完全一样。
**预期提升**: 跨域 +8-15%，对抗 +10-20%。

**与 DEFACTIFY data noising 的区别**:
- DEFACTIFY (arXiv 2502.16857) 是静态 10% 噪声注入，简单但效果有限
- DP-Net 用 RL 动态生成扰动，更精准地模拟真实域偏移
- 建议：先做 DEFACTIFY（简单），再升级到 DP-Net

---

### 方案 F：DivEye 高阶统计特征（零成本，已有基础设施）

**论文**: Basani & Chen, "Diversity Boosts AI-Generated Text Detection", TMLR 2026
- https://arxiv.org/abs/2509.18880
- https://github.com/IBM/diveye

**方法**: 计算 surprisal 序列的 4 个高阶统计量（方差、熵、峰度、偏度），作为零样本检测信号。

**关键数字**:
- 比所有零样本方法强 **33.2%**
- 跨模型泛化好（不需要知道生成器）
- 对 paraphrase 鲁棒（看的是 surprisal 分布形状，不是具体值）

**为什么还没做**: 之前 CLAUDE.md 里有 action item 但未执行。

**成本**: $0。你已有 qwen3.5:4b 的 surprisal 数据。
**CPU 可行性**: 纯统计计算，ms 级。
**预期提升**: 作为 ensemble 辅助信号，LR 从 82% → **88-92%**。

---

### 方案 G：PHD 持久同调维度（低成本，CPU 可行）

**论文**: Tulchinskii et al., "Intrinsic Dimension Estimation for Robust Detection of AI-Generated Texts", NeurIPS 2023
- https://openreview.net/forum?id=8uOZ0kNji6
- https://github.com/tolgabirdal/PHDimGeneralization

**方法**: 用 RoBERTa-base (125M params) 提取文本 embedding，计算持久同调维度（PHD）。人类文本固有维度 ~9，AI 文本 ~7.5。

**关键数字**:
- **paraphrase-resistant**（改写后维度不变，因为衡量的是信息复杂度而非表层词汇）
- 人类 PHD ~9 vs AI PHD ~7.5（可分离）
- 对 ESL 写作偏见低

**成本**: 需要 RoBERTa-base 推理（~500MB，CPU 可行但慢）。
**CPU 可行性**: 可行但单次推理 ~2-5 秒（vs DeBERTa ~0.5 秒）。可异步计算。
**预期提升**: 作为正交信号对 paraphrase 攻击特别有效，+5-8%。

**权衡**: 额外加载一个 125M 模型，Railway RAM 需要足够。

---

### 方案 H：RADAR 对抗训练框架（中等成本，需 GPU）

**论文**: Hu, Chen & Ho, "RADAR: Robust AI-Text Detection via Adversarial Learning", NeurIPS 2023
- https://arxiv.org/abs/2307.03838
- https://github.com/IBM/RADAR

**方法**: 联合训练 paraphraser + detector。Paraphraser 生成逃检文本，detector 反过来用这些样本增强自己。GAN 式对抗训练。

**关键数字**:
- 面对未见过的 GPT-3.5-Turbo paraphraser，AUROC 比最佳已有检测器提升 **+31.64%**
- 跨 8 个 LLM × 4 数据集验证

**成本**: 训练需要 GPU（Colab T4 ~4-6 小时）+ paraphraser LLM 推理成本。
**CPU 可行性**: 训练完后 detector 推理与普通 DeBERTa 一样。
**预期提升**: 对抗场景 +20-30%。

**与你的 StealthRL 的关系**: StealthRL 训练 attacker（humanizer），RADAR 训练 defender（detector）。两者互补——先用 StealthRL 生成对抗样本，再用 RADAR 思路训练 detector。

---

### 方案 I：ModernBERT 替换 DeBERTa（低优先级）

**论文**: "ModernBERT or DeBERTaV3? Examining Architecture and Data Influence"
- https://arxiv.org/abs/2504.08716

**关键数字**:
- ModernBERT 推理速度 **2x faster** than DeBERTa
- 内存占用 **<1/5** of DeBERTa
- GLUE 分数略优于 DeBERTa-v3
- 但: 控制数据集差异后，DeBERTa-v3 仍然 sample efficiency 更好

**成本**: Colab 重训 ~3 小时。
**为什么低优先级**: 推理速度不是瓶颈（Railway CPU 推理 DeBERTa 已够用），收益主要在内存和速度，不在检测准确率。

---

### 方案 J：DeepSeek API 零样本辅助信号（$1-3/月）

**方法**: 用 DeepSeek V3 ($0.14/M input tokens) 做零样本判断，作为 ensemble 的一个投票者。

**计算成本**:
- 每次检测发送 ~500 tokens → $0.00007/次
- 1000 次/月 → $0.07/月
- 即使 10000 次/月也只 $0.7

**实施方式**:
```
Prompt: "Does this text read like it was written by a human or generated by AI?
Respond with a confidence score 0-100 (0=definitely human, 100=definitely AI).
Consider: naturalness of transitions, specificity of examples,
presence of filler phrases, and stylistic consistency."
```

**预期收益**: LLM-as-judge 在简单文本上准确率 ~70-80%，作为 ensemble tie-breaker 有效。
**风险**: 延迟增加（API round-trip ~1-2s），不适合做主要信号。

---

## 三、ONNX Runtime INT8 量化加速（基础设施优化）

**来源**: Microsoft ONNX Runtime 文档 + 实践案例
- https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html
- https://serkanaytekin.com/from-deberta-to-onnx-with-microsoft-olive-and-onnxruntime/

如果同时加载 v1 + v3 两个 DeBERTa，内存和延迟是关键约束。

**方法**: 导出 DeBERTa 为 ONNX → 动态 INT8 量化。

**关键数字**:
- 模型大小 **~4x 压缩**（738MB → ~185MB per model）
- CPU 推理速度 **2-3x 提升**
- 精度损失 **<0.5%**（分类任务）

**实施**:
```python
from optimum.onnxruntime import ORTQuantizer, ORTModelForSequenceClassification
from optimum.onnxruntime.configuration import AutoQuantizationConfig

model = ORTModelForSequenceClassification.from_pretrained("models/detector_v1/", export=True)
quantizer = ORTQuantizer.from_pretrained(model)
qconfig = AutoQuantizationConfig.avx512_vnni(is_static=False)  # 动态量化
quantizer.quantize(save_dir="models/detector_v1_int8/", quantization_config=qconfig)
```

**成本**: $0，本地执行。
**建议**: 在做 ensemble 之前先做这个，为同时加载两个模型腾出空间。

---

## 四、推荐实施路线图

### Phase 1: 零成本快赢（本周，0-3 天）

| 步骤 | 方案 | 预期效果 | 成本 |
|------|------|----------|------|
| 1.1 | ONNX INT8 量化 v1 + v3 | 两模型共 ~370MB，推理 2-3x 快 | $0 |
| 1.2 | DivEye 高阶统计特征 (F) | PPL-based 信号从 82% → 88% | $0 |
| 1.3 | Confounding Neuron Suppression (A) | OOD +6.9% | $0 |

**Phase 1 预期**: 总体从 50-72% → **65-78%**

### Phase 2: v1/v3 Ensemble + 路由（第 1-2 周）

| 步骤 | 方案 | 预期效果 | 成本 |
|------|------|----------|------|
| 2.1 | 收集 500+ 跨域标注数据 | 法律/创意/代码/学术 | DeepSeek ~$2 |
| 2.2 | TF-IDF+LR Genre Router (B) | 域感知路由 | $0 |
| 2.3 | Platt Scaling 校准 (B) | 置信度可靠 | $0 |
| 2.4 | PIFE 对抗检测 (C) | 对抗 33% → 65% | $0 |

**Phase 2 预期**: 总体 **75-85%**

### Phase 3: 深度信号 + 对抗训练（第 2-3 周）

| 步骤 | 方案 | 预期效果 | 成本 |
|------|------|----------|------|
| 3.1 | DP-Net 动态扰动重训 (E) | 泛化 +15%, 对抗 +20% | Colab T4 |
| 3.2 | PHD 持久同调维度 (G) | paraphrase-resistant 正交信号 | $0 |
| 3.3 | XGBoost Meta-Learner | 融合所有信号的最终决策 | $0 |
| 3.4 | DeepSeek 零样本 tie-breaker (J) | 边界case 兜底 | ~$1/月 |

**Phase 3 预期**: 总体 **82-90%**

---

## 五、v1/v3 Ensemble 可行性深度分析

### 为什么 ensemble 比重训一个新模型更好

1. **互补性验证**: v1 对抗 100% + v3 human 83% = oracle ceiling 接近 90%
2. **零训练成本**: 两个模型都已训好
3. **理论支持**: DoGEN (Tripathi et al., 2025) 证明 domain gating ensemble 用小模型(1.8B×2)超过 32B 单模型

### 内存预算

| 组件 | 内存 (INT8) | 备注 |
|------|------------|------|
| DeBERTa v1 | ~185MB | INT8 量化 |
| DeBERTa v3 | ~185MB | INT8 量化 |
| TF-IDF + LR Router | ~5MB | scikit-learn |
| SentenceTransformer | ~90MB | PIFE 用 |
| XGBoost Meta-Learner | ~1MB | |
| **总计** | **~466MB** | Railway 1GB 以内 |

### 路由策略详细设计

```python
def detect(text: str) -> float:
    genre = router.predict(text)  # essay/creative/professional/adversarial

    v1_score = deberta_v1.predict(text)  # Platt-calibrated
    v3_score = deberta_v3.predict(text)  # Platt-calibrated
    pife_delta = compute_pife_features(text)
    divey_stats = compute_diveye_features(surprisal_seq)

    features = [v1_score, v3_score, genre_onehot, pife_delta, divey_stats]

    final_score = xgboost_meta.predict(features)
    return final_score
```

---

## 六、跨域数据生成策略

### 用 DeepSeek 批量生成跨域 AI 样本

**成本计算**:
- 每条样本 ~300 tokens output → $0.14 × 0.3 / 1000 = $0.000042/条
- 10,000 条 = **$0.42**
- 6 个域 × 5 个 prompt 风格 × 4 个长度 = 120 种组合

**域覆盖计划**:

| 域 | 样本数 | 来源 |
|----|--------|------|
| Essay/Academic | 已有 80K | 现有数据 |
| 法律文书 | 2,000 | DeepSeek 生成 + 公开法律文本 |
| 创意写作 | 2,000 | DeepSeek 生成 + Project Gutenberg/Reddit WritingPrompts |
| 代码评审/技术文档 | 2,000 | DeepSeek 生成 + StackOverflow |
| 商务邮件 | 1,000 | DeepSeek 生成 + Enron Corpus |
| 社交媒体/口语化 | 1,000 | DeepSeek 生成 + Twitter/Reddit |
| 新闻报道 | 1,000 | DeepSeek 生成 + CNN/DailyMail |

**Human 数据来源** (免费):
- MIRAGE benchmark (arXiv 2509.14268): 93K 样本，17 LLMs，5 域
- Project Gutenberg: 创意写作
- Enron Corpus: 商务邮件
- StackOverflow dumps: 技术文档
- FAQS 和 wiki: 百科风格

---

## 七、风险与 Mitigation

| 风险 | 概率 | 影响 | Mitigation |
|------|------|------|------------|
| INT8 量化损失 > 1% | 低 | 准确率下降 | 先在红队集上验证，不行就用 FP16 |
| v1+v3 同时加载 OOM (Railway) | 中 | 部署失败 | INT8 量化后总共 ~466MB，应该没问题；否则用模型切换而非同时加载 |
| Genre Router 错误路由 | 中 | 性能下降 | soft routing (weighted average) 作为 fallback |
| PIFE 标准化管线延迟过高 | 低 | 用户体验差 | 异步计算，先返回 DeBERTa 结果，PIFE 结果作为补充 |
| 新 LLM (GPT-5 等) 逃过所有检测 | 高 | 根本性挑战 | 多信号 ensemble 比单一模型更 robust；DeTeCtive TFIA 可快速适配 |

---

## 八、与商业系统对标

| 系统 | 架构 | 我们的对标方案 |
|------|------|---------------|
| GPTZero 7 组件 | burstiness + sentence classifier + PPL + education + internet search + adversarial shield + DL | DivEye(burstiness++) + SentenceAnalysis(已有) + PPL(已有) + PIFE(adversarial) + DeBERTa ensemble(DL) = **5/7 组件** |
| Pangram 硬负例挖掘 | synthetic mirrors + FP mining | RADAR 对抗训练 + Phase 2 FP calibration |
| Turnitin 双模型 | AIW-2 (primary) + AIR-1 (paraphrase-specific) | v1 (primary) + v3 (domain-specific) + PIFE (paraphrase-aware) |
| Originality.ai | ELECTRA + Red team loop | DP-Net 动态扰动 + StealthRL 红队对抗 |

---

## 参考论文汇总

| 论文 | 会议/期刊 | 年份 | 核心贡献 | 对我们的价值 |
|------|-----------|------|----------|-------------|
| Confounding Neurons (Borile & Abrate) | EMNLP Findings | 2025 | Post-hoc neuron suppression, +6.9% OOD | 零成本，立即可做 |
| MoSEs (Wu et al.) | EMNLP | 2025 | Stylistics-Aware Router, +11.3%/+39.2% | Genre router 设计参考 |
| DoGEN (Tripathi et al.) | arXiv | 2025 | Domain Gating Ensemble, 95.8% AUROC | Ensemble 架构验证 |
| PIFE (arXiv 2510.02319) | arXiv | 2025 | Perturbation quantification, 82.6% TPR@1%FPR | 对抗检测核心方案 |
| DP-Net (Zhou et al.) | NAACL | 2025 | RL dynamic perturbations, dual SOTA | 重训方案首选 |
| DivEye (Basani & Chen) | TMLR | 2026 | Surprisal diversity, +33.2% zero-shot | 已有基础，零成本 |
| DeTeCtive (He et al.) | NeurIPS | 2024 | TFIA, +7% OOD without retraining | 快速域适配 |
| RADAR (Hu, Chen & Ho) | NeurIPS | 2023 | Adversarial training, +31.64% AUROC | 对抗训练参考 |
| PHD (Tulchinskii et al.) | NeurIPS | 2023 | Intrinsic dimensionality, paraphrase-resistant | 正交信号 |
| DEFACTIFY (arXiv 2502.16857) | arXiv | 2025 | 10% noise injection, F1=1.0 | 简单 data noising baseline |
| Detecting the Machine (arXiv 2603.17522) | arXiv | 2026 | Comprehensive benchmark, no method generalizes | 问题诊断佐证 |
| FAID (EACL 2026) | EACL | 2026 | Multi-task + contrastive, unseen domain adapt | 架构参考 |
| ModernBERT vs DeBERTa (arXiv 2504.08716) | arXiv | 2025 | 2x faster, 1/5 memory, similar accuracy | 低优先级替换选项 |

---

## 结论

**最大杠杆点**: v1/v3 Ensemble + Genre Router (方案 B)。这是唯一不需要任何训练、不需要 GPU、不花钱，就能把 50% 和 72% 两个模型合成接近 80% 的方案。

**第二杠杆点**: PIFE (方案 C) 专治 v3 对抗崩溃问题。

**长期方向**: DP-Net 重训 (方案 E) 从根本上解决泛化+鲁棒双重问题，是下一次 Colab 训练的首选方案。

三个阶段总预算: **< $5**（主要是 DeepSeek 生成跨域数据的成本）。预期将红队总分从 50-72% 提升到 **82-90%**。
