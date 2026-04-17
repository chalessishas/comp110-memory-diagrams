# Research Loop 00:00 — ai-text-detector v6 重启路径

**时间**：2026-04-17 00:01 (跨日首次 Research Loop)
**触发**：Opus fleet converged on TOEFL/Signal-Map 后，切到 P4 候选之一（ai-text-detector，12 天未动）
**Parent 自跑 WebSearch × 3**（避免 agent 超时风险）

---

## 1. 研究方向

ai-text-detector 项目 STATUS.md 最后更新 2026-04-06，dataset_v6.jsonl (1.25GB) 已生成但 DeBERTa v6 尚未重训。11 天停滞。本报告回答："**恢复训练前需要验证哪些 2026 新发现的失败模式，避免 v6 重复 v5 的坑**"。

---

## 2. 2026 外部证据

### E1. 检测器对不同模型家族的准确率差异显著
2026 benchmark 显示：GPT-4o 91% / Claude 3.5 87% / Gemini Pro 84% / Llama 3 79%。**意味着 v6 训练集里如果偏某一家族，对其他家族泛化会下降 7-12%**。
URL: https://www.undetectedgpt.ai/blog/ai-detection-2026

### E2. Adversarial 攻击下准确率崩盘至 17.4%
Top detector 清洁文本 96-98% → humanized 60-70% → basic adversarial 17.4%。**v5 踩的"连贯性伪相关"坑本质就是 adversarial blind spot 之一**。
URL: https://textshift.blog/blog/ai-detector-accuracy-benchmark-2026-real-test-results-compared/

### E3. PADBen — 专测 paraphrase 攻击的新 benchmark（2025-11）
arxiv 2511.00416 引入 PADBen，测试的 findings："detectors successfully identify plagiarism evasion but fail for authorship obfuscation"。**v6 应该加入 PADBen-style 对抗 eval 而不是只看清洁集 accuracy**。
URL: https://arxiv.org/html/2511.00416

### E4. 检测器间的商业 benchmark 差异极大
GPTZero 100% 检测 GPT-5，Originality AI 只 31.7%，而且 GPT-5-mini 检测率仅 7.3%。**意味着不同检测器架构选择 ×10 效果差异，v6 需对标 GPTZero-style 的集成不是单一 DeBERTa**。
URL: https://fritz.ai/gptzero-vs-originality/

### E5. NVIDIA quality-classifier-deberta 参考基线（22.8K 样本 82.5%）
URL: https://huggingface.co/nvidia/quality-classifier-deberta
证明 DeBERTa v3 base + ~22K 样本即可达 82.5%。v6 有 70K+ 样本应该有空间到 88-92%。

### E6. Unsloth 的 2026 Feb 训练加速（250+ notebook）
URL: https://github.com/unslothai/notebooks
但 CLAUDE.md 记录 2026-03-21 的经验是 "avoid unsloth"。**保持这条原则**——unsloth 的加速在新模型适配上有兼容性历史问题。用原生 HuggingFace trainer。

### E7. Data contamination awesome list
URL: https://github.com/lyy1994/awesome-data-contamination
值得在训练前扫一次，检查 v6 数据集是否无意污染进 held-out eval set。

---

## 3. v6 重启前的数据质量 3-check

### Check 1: 连贯性（修复 v5 坑）
v5 的失败根因 STATUS.md 已记录："random shuffled human texts"。**验证**：从 dataset_v6.jsonl 抽样 50 条 label=0 (human) + 50 条 label=1 (AI)，人工肉眼过一遍检查 human 是否**段内连贯**（不应出现"法语翻译混八卦"这种拼接）。

### Check 2: 模型家族分布
STATUS.md 说"23 models × 6 styles × 20 topics"。**验证**：`jq '.source' dataset_v6.jsonl | sort | uniq -c` 看每模型家族样本数。警戒线：某一家族（如 GPT）占比 > 50% → 可能导致 E1 的 7-12% 泛化损失。

### Check 3: 时间戳去污染
E7 提示：`dataset_v6.jsonl` 生成于 2026-04-06，如果 benchmark 集来自公开 corpus（C4、Wikipedia），有 pre-2019 cutoff 的 overlap 风险。`scripts/build_corpus_colab.py` 已有 2019 cutoff 控制 — 验证 v6 dataset 也遵守。

---

## 4. 训练时增加的 2026-style evaluation

当前 tests/ 有 test_detector.py (27 cases) + test_redteam.py (35 adversarial)。**建议增加**：

- **PADBen-style**: 对每条 AI 样本自动 paraphrase（用 DeepSeek 或 Qwen）得 paraphrased 样本，测模型在此子集 accuracy。预期 ≥ 60%。
- **Model-family eval**: 对 6 个家族（GPT-4o / GPT-5 / Claude 3.5 / Claude 4.x / Gemini 2.5 / Llama 3）各 100 条，分别报告 per-family accuracy。目标：任何家族不低于 80%。
- **Mixed content eval**: 50 条 AI 50% + human 50% 混合段落，模型应给 middle score (0.3-0.7)，避免二元化。

---

## 5. 恢复训练的 4 步路径

| 步骤 | 时间 | 资源 | 主人动作 |
|-----|------|------|---------|
| 1. 数据 3-check (§3) | 20 分钟 | 本机 | 跑 3 个 `jq`/sampling 脚本，肉眼过 100 条 |
| 2. 新 eval script（§4） | 30 分钟 | 本机 | 写 3 个 python 测试，dataset_v6 上跑 |
| 3. Colab A100 训练 | 30-60 分钟 | **Colab A100 slot** | 上传 dataset_v6.jsonl 到 Drive，跑 `train_detector_v5_colab.ipynb`（改名 v6）|
| 4. 验证 + 部署 | 15 分钟 | 本机 | 下载模型到 `models/detector_v6/`，跑全 eval |

**总耗时预估：1h40m - 2h25m**（其中 30-60 分钟 Colab GPU 可 unattended）。

---

## 6. 不做的事

- **不启动自动化 GitHub Actions + Colab**（E6 研究发现）：Colab 不支持 headless 授权，GitHub Actions + Colab 集成需要 token 危险暴露。**主人手动启动 Colab 仍然是最简路径**。
- **不引入 unsloth**（E6 明确避免）。
- **不换更大 DeBERTa**（v3 base 足够达到 NVIDIA baseline 的 82.5%，上 v3 large 会翻倍 GPU memory 风险 Colab OOM）。

---

## 7. 本次 Research Loop 的 next command（给主人）

最小启动路径（20 分钟就能判断 v6 是否值得训）：
```bash
cd "/Users/shaoq/Desktop/VScode Workspace/ai-text-detector"
# Check 1: 抽样 10 条 human 看连贯性
jq -c 'select(.label==0) | .text' dataset_v6.jsonl | head -10 | less

# Check 2: 模型家族分布
jq -r 'select(.label==1) | .model // .source // "unknown"' dataset_v6.jsonl | sort | uniq -c | sort -rn

# Check 3: 时间戳（如果有 date field）
jq -r '.created_at // .year // "none"' dataset_v6.jsonl | sort -u | head -20
```

如果 Check 1/2/3 任何一项不通过 → 修数据集而不是训练。
如果都通过 → 进入 Colab 训练步骤 3。

---

## Sources

- [AI Detection 2026 — model family accuracy](https://www.undetectedgpt.ai/blog/ai-detection-2026)
- [AI Detector Accuracy Benchmark 2026 — adversarial drop](https://textshift.blog/blog/ai-detector-accuracy-benchmark-2026-real-test-results-compared/)
- [PADBen benchmark (arxiv 2511.00416, 2025-11)](https://arxiv.org/html/2511.00416)
- [GPTZero vs Originality 2026](https://fritz.ai/gptzero-vs-originality/)
- [NVIDIA quality-classifier-deberta](https://huggingface.co/nvidia/quality-classifier-deberta)
- [Unsloth notebooks repo (2026-02 update)](https://github.com/unslothai/notebooks)
- [awesome-data-contamination](https://github.com/lyy1994/awesome-data-contamination)
