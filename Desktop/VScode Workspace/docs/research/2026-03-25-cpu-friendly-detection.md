# CPU-Friendly AI 文本检测方法：2025-2026 最新方案

> 日期: 2026-03-25
> 背景: AI Text X-Ray 当前使用 DeBERTa-v3-base，CPU-only 部署在 Railway，红队准确率 54.4%
> 目标: 在不增加 GPU 开支的前提下显著提升检测准确率

---

## 一、现状问题总结

| 弱项 | 当前表现 | 根因 |
|------|----------|------|
| Academic human 误判 | 80% false positive | DeBERTa 过拟合 essay 风格，学术文体被当成 AI |
| Short tweet 漏检 | 100% miss | <50 词信号不足，已加 uncertain 门槛但治标不治本 |
| Business human 误判 | 60% false positive | 正式文体偏见 |

---

## 二、立即可用方案（零成本 / CPU-only）

### 方案 1：轻量级 Stylometric 特征 + LightGBM（无需神经网络）

**来源**:
- [A Lightweight Approach to Detection of AI-Generated Texts Using Stylometric Features](https://arxiv.org/abs/2511.21744) (2025)
- [Old N-Grams Never Die: Towards Identifying LLMs](https://openreview.net/pdf/14ae05281ea468a284d570a13e22585e64c93e56.pdf) (2025)
- [StylOch at PAN: Gradient-Boosted Trees with Frequency-Based Stylometric Features](https://arxiv.org/html/2507.12064v1) (2025)

**方法**:
从文本中提取纯统计特征，用 LightGBM 分类，完全不需要 transformer 推理：
- **词汇多样性**: Type-Token Ratio, Hapax Legomena ratio
- **句法特征**: 平均句长、句长标准差、POS bigram 频率
- **节奏/Burstiness**: 句长序列的方差和峰度（人类文本 burstiness 更高）
- **N-gram 频率**: 字符 3-gram、词 2-gram 频率分布
- **功能词频率**: 虚词（the, of, in）使用模式
- **标点模式**: 逗号/句号密度、分号使用率

**关键数据**:
- 准确率 79%-98%（取决于域），Wikipedia vs GPT-4 达到 .98
- 轻量级 stylometric + self-attention 分类器在短评论检测上 F1=91.8%
- 推理时间：纯统计计算 + LightGBM，单次 <5ms（比 DeBERTa 快 100x）

**CPU 成本**: $0。spaCy + scikit-learn + lightgbm 即可。

**实施步骤**:
1. 用 spaCy 做 tokenization 和 POS tagging（`en_core_web_sm`，15MB）
2. 提取 ~50 个统计特征（词汇、句法、节奏、n-gram）
3. 用已有的训练数据训练 LightGBM 分类器
4. 作为 ensemble 的第三路信号，与 DeBERTa v1/v3 组合

**预期提升**: 作为独立分类器 ~80%；作为 ensemble 信号 +5-10%，特别是减少 academic human 误判（因为 stylometric 特征不受文体影响）。

---

### 方案 2：DeBERTa ONNX INT8 量化（加速现有模型）

**来源**:
- [DeBERTa-v3-NLI-ONNX-Quantized](https://model.aibase.com/models/details/1915693925207269378)
- [Optimizing BERT for Intel CPU using ONNX Runtime](https://opensource.microsoft.com/blog/2021/03/01/optimizing-bert-model-for-intel-cpu-cores-using-onnx-runtime-default-execution-provider)
- [Faster and Smaller Quantized NLP with HuggingFace and ONNX Runtime](https://medium.com/microsoftazure/faster-and-smaller-quantized-nlp-with-hugging-face-and-onnx-runtime-ec5525473bb7)

**方法**:
将现有 DeBERTa-v3-base 转换为 ONNX 格式，再做 INT8 动态量化：

```
PyTorch DeBERTa → ONNX export → INT8 dynamic quantization → ONNX Runtime inference
```

**关键数据**:
- 模型大小：~370MB → ~93MB（4x 压缩）
- 推理速度：2-3x 加速（有 AVX2 的 CPU 上），VNNI CPU 上最高 6x
- 精度损失：通常 <1% F1

**CPU 成本**: $0。减少 Railway 内存和 CPU 占用。
**部署影响**: 可以同时加载 v1 + v3 的量化版本，节省内存空间给 ensemble。

**实施步骤**:
1. `pip install optimum onnxruntime`
2. `optimum-cli export onnx --model your-deberta-model --task text-classification`
3. 用 `onnxruntime.quantization` 做 INT8 动态量化
4. 替换 PyTorch 推理为 ONNX Runtime

---

### 方案 3：Fast-DetectGPT 零样本检测（补充信号）

**来源**:
- [Fast-DetectGPT: Efficient Zero-Shot Detection](https://arxiv.org/abs/2310.05130) (ICLR 2024)
- [GitHub: fast-detect-gpt](https://github.com/baoguangsheng/fast-detect-gpt)
- [Demo: fastdetect.net](https://fastdetect.net)

**方法**:
计算文本的条件概率曲率（conditional probability curvature），不需要训练数据：
1. 用一个小型 LM（GPT-2 124M 或 Qwen 0.5B）计算文本的 token-level log probabilities
2. 用采样替代扰动（比 DetectGPT 快 340x）
3. 计算概率曲率作为检测信号

**关键数据**:
- 比 DetectGPT 快 340x，准确率高 75%
- 零样本，不需要任何训练数据
- 对新模型泛化好（不依赖特定训练分布）

**CPU 可行性**:
- GPT-2 124M 可以在 CPU 上运行，单次推理 ~2-5 秒
- 但如果用更大模型（GPT-2 XL 或 Qwen），会显著变慢
- 最佳方案：用 ONNX 量化的 GPT-2-small 做 scoring model

**成本**: $0（用本地小模型）或 ~$0.01/请求（用 API）

**适合场景**: 作为第二路零样本信号，与 DeBERTa 的有监督信号互补。特别适合检测新模型生成的文本（DeBERTa 可能没见过的分布）。

**权衡**: CPU 上 GPT-2 推理较慢（2-5秒），可能需要异步处理。

---

### 方案 4：Hybrid Ensemble — 三路投票系统

**来源**:
- [A Theoretically Grounded Hybrid Ensemble for Reliable Detection](https://arxiv.org/html/2511.22153v1) (2025)
- [Using Aggregated AI Detector Outcomes to Eliminate False Positives](https://journals.physiology.org/doi/full/10.1152/advan.00235.2024)

**方法**:
将上述方法组合为三路 ensemble：

```
输入文本
  ├── Path 1: DeBERTa v1/v3 ensemble (有监督, ~0.5s)
  ├── Path 2: Stylometric LightGBM (统计, ~5ms)
  └── Path 3: DivEye 高阶统计量 (零样本, ~10ms)
       ↓
  F1-optimized weighted fusion (Platt-scaled)
       ↓
  最终判定
```

**关键数据**:
- 论文中的三路 ensemble（RoBERTa + GPT-2 perplexity + statistical）达到 94.2% 准确率
- **False positive 减少 35%**（核心指标：解决 academic human 误判）
- 只在多路一致时才判定 AI，大幅降低误报

**为什么这是最优方案**:
1. DeBERTa 捕捉文本的深层语义模式
2. Stylometric 特征不受文体影响，纠正 DeBERTa 的文体偏见
3. DivEye 的 surprisal 统计量是正交信号，对 paraphrase 鲁棒
4. 三路投票天然降低 false positive（需要 ≥2 路同意）

**实施优先级**:
1. 先做 Stylometric LightGBM（1-2 天，零成本）
2. 再做 DivEye 集成（1 天，已有 surprisal 基础设施）
3. 然后做 ONNX 量化（1 天，加速现有模型）
4. 最后考虑 Fast-DetectGPT（需要额外模型加载）

---

## 三、中期方案（1-3 周）

### 方案 5：知识蒸馏 — DeBERTa → TinyBERT/MiniLM

**来源**:
- [TinyBERT: Distilling BERT for NLU](https://arxiv.org/abs/1909.10351)
- [DeBERTa Comprehensive Guide 2025](https://www.shadecoder.com/topics/deberta-a-comprehensive-guide-for-2025)

**方法**:
将 DeBERTa-v3-base (184M params) 蒸馏为 TinyBERT (14.5M params) 或 MiniLM (33M params)：
- 模型缩小 5-12x
- 推理快 7-9x
- 精度保持 90-95%

**意义**: 释放 CPU/RAM 预算给 ensemble 中的其他组件。目前一个 DeBERTa ~370MB，量化后 ~93MB。但如果蒸馏到 MiniLM，只需 ~66MB，可以同时加载 4-5 个小模型做 ensemble。

---

### 方案 6：Binoculars — 双模型零样本检测

**来源**:
- [Spotting LLMs With Binoculars](https://arxiv.org/abs/2401.12070) (ICML 2024)
- [GitHub: ahans30/Binoculars](https://github.com/ahans30/Binoculars)

**方法**:
用两个 LM（observer + performer）计算 perplexity/cross-perplexity 比值：
- 90%+ 检测率，0.01% false positive rate
- 零样本，不需要训练

**CPU 限制**: 需要加载两个 LM（至少 GPT-2 level），CPU 上会很慢（10-30秒）。
**折中方案**: 只对 DeBERTa 置信度低（0.4-0.6）的样本触发 Binoculars 二次检测，减少调用频率。

---

## 四、推荐执行路线图

| 阶段 | 方案 | 时间 | 成本 | 预期提升 |
|------|------|------|------|----------|
| **Week 1** | Stylometric LightGBM + DivEye 集成 | 2-3 天 | $0 | 54% → 65-70% |
| **Week 1** | ONNX INT8 量化 | 1 天 | $0 | 推理速度 2-3x，内存 4x 减少 |
| **Week 2** | 三路 ensemble 融合 + Platt scaling | 2-3 天 | $0 | 70% → 75-80% |
| **Week 3** | Genre router（已在 detection-improvement-plan 中） | 2-3 天 | $0 | 80% → 82-85% |
| **Month 2** | Fast-DetectGPT 异步 + 知识蒸馏 | 1-2 周 | $0-5 | 85% → 88-90% |

**总预算**: $0-5
**总时间**: 4-6 周
**预期最终红队准确率**: 85-90%（从当前 54.4%）

---

## 五、针对具体弱项的对策

### Academic Human 误判 80% → 目标 <20%

核心问题：DeBERTa 将"正式文体"等同于"AI 生成"。

**对策**:
1. **Stylometric 特征**可以区分"正式但有人类节奏"和"正式且单调"（burstiness, 句长方差）
2. **DivEye**的 surprisal 偏度/峰度在 academic human 上呈现长尾分布，与 AI 的正态分布不同
3. **三路投票**：即使 DeBERTa 误判，另两路会纠正

### Short Tweet 漏检 → 目标 >50%

核心问题：50 词以下信号不足。

**对策**:
1. 短文本用 **Stylometric-only** 路径（不依赖 DeBERTa）
2. 关键特征：词汇多样性、标点密度、emoji 使用模式
3. 研究显示 stylometric F1=91.8% 在短评论上，比 transformer 在短文本上更可靠

### Business Human 误判 60% → 目标 <25%

核心问题：与 academic 类似，正式文体偏见。

**对策**: 同 academic human，stylometric + DivEye 纠偏。business 文本的 burstiness 虽然比 casual 低，但仍比 AI 高。

---

## Sources

- [A Lightweight Approach to Detection of AI-Generated Texts Using Stylometric Features](https://arxiv.org/abs/2511.21744)
- [Old N-Grams Never Die: Towards Identifying LLMs](https://openreview.net/pdf/14ae05281ea468a284d570a13e22585e64c93e56.pdf)
- [StylOch at PAN: Gradient-Boosted Trees with Frequency-Based Stylometric Features](https://arxiv.org/html/2507.12064v1)
- [Fast-DetectGPT: Efficient Zero-Shot Detection](https://arxiv.org/abs/2310.05130)
- [Spotting LLMs With Binoculars](https://arxiv.org/abs/2401.12070)
- [A Theoretically Grounded Hybrid Ensemble for Reliable Detection](https://arxiv.org/html/2511.22153v1)
- [Using Aggregated AI Detector Outcomes to Eliminate False Positives](https://journals.physiology.org/doi/full/10.1152/advan.00235.2024)
- [DeBERTa-v3-NLI-ONNX-Quantized](https://model.aibase.com/models/details/1915693925207269378)
- [Optimizing BERT for Intel CPU](https://opensource.microsoft.com/blog/2021/03/01/optimizing-bert-model-for-intel-cpu-cores-using-onnx-runtime-default-execution-provider)
- [TinyBERT: Distilling BERT for NLU](https://arxiv.org/abs/1909.10351)
- [DivEye: Diversity Boosts AI-Generated Text Detection](https://arxiv.org/abs/2509.18880)
