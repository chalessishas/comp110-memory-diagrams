# 踩坑经验总册

> 跨项目的教训记录。每条都是真金白银（时间、GPU 费、精力）换来的。新对话、新项目前先扫一遍。
>
> 最后更新: 2026-04-09

---

## 一、工作流 & 协作

### 1. 数据质量先于数量
先逐个验证每个数据源能用（load + 抽 1 条 + 确认字段），再跑全量收集。题材多样性 > 总量——100K 覆盖 30 个题材远好过 600K 只有 3 个题材。

**代价**：2026-04-05，49 个 HF 数据源有 24 个因 `Dataset scripts are no longer supported` 完全失败，浪费 3+ 小时和 RunPod 费用。

### 2. 审查要问"在哪会失败"
代码审查不能只找表面 bug。必须问：训练数据覆盖了什么、缺了什么？测试集能否捕捉核心问题？"全绿"是真好还是过拟合？架构假设在生产中成立吗？

**代价**：2026-04-06，用户用 8 个问题在 5 分钟内定位了我几天没发现的盲区（ESL 缺失、student_essay 仅 63 条、DANN 域标签可能无效），而 AI 的 Explore Agent 只做了代码级扫描。

### 3. 编年记录每个 turn 都写
每个 turn 结束写 `docs/chronicle/YYYY-MM-DD.md`，用 `date '+%Y-%m-%d %H:%M:%S'` 取真实时间戳。不攒批、不延后、不跳过。

**代价**：每次新对话都"忘了"，用户多次提醒。

### 4. 技术决策自己拍板
所有技术选择（模型、参数、架构、修复方案）自己做决定。只在需要密码/API key/付款时才找用户。

**代价**：用户被反复打断休息，非常不满。

---

## 二、GPU 训练 & 云服务

### 5. Colab 文件传输走 Google Drive
本地 → Drive 上传 → Colab cell 里 `drive.mount('/content/drive')` → cp 到 /content/。**不要在 terminal 里跑 drive.mount**（报 `AttributeError: 'NoneType' object has no attribute 'kernel'`）。不要试 SCP/SSH/HTTP server——Colab 没有公网 SSH。

**代价**：2026-04-06，浪费 3+ 小时在文件传输上。

### 6. Colab A100 免费但会断
免费 Colab A100 是训练首选，但有 90 分钟空闲断连 + 12 小时最长会话限制。长时间训练要定期检查是否还活着。

### 7. RunPod 操作清单
- **先下载模型再删 pod**——2026-04-05 StealthRL LoRA 因 pod 提前删除而丢失
- **pin 依赖版本，一次装完**——反复 pip install 不同版本容易冲突
- **避免 unsloth**——和 torch/transformers 版本三角冲突严重，用标准 PEFT + TRL
- **新显卡（5090 等）慎用**——驱动和库可能不兼容，SSH 启动 15+ 分钟
- **Secure Cloud A100 启动快**——Community Cloud 可能排队但更便宜

### 8. RTX 5090 不兼容 PyTorch 2.4
Blackwell sm_120 架构需要 PyTorch 2.6+。L40S 需要 CUDA 12.4+ driver。选 GPU 前先确认框架兼容性。

---

## 三、AI 检测器（ai-text-detector）

### 9. DeBERTa fp16 会爆
必须 `model.float()` 用 fp32。M-series Mac 和 Colab 上 DeBERTa-v3 跑 fp16 都会 NaN。

### 10. tokenizer_config.json 跨版本不兼容
Colab transformers 5.x 保存 `extra_special_tokens` 为 list；本地 4.x 需要 `additional_special_tokens: []`。迁移模型时注意检查。

### 11. DeBERTa 跨域 AUROC 只有 0.5-0.6
本质上在没见过的域上和随机猜一样。学的是模型指纹，不是通用 AI 特征。不要对 DeBERTa 单独的跨域能力抱期望。

### 12. PPL 的人类范围是模型特定的
不要从论文里抄阈值。必须用检测时实际使用的同一模型在 dataset.jsonl 上校准。

### 13. 换 PPL 模型必须重训 LR
切换 PPL 模型（如 llama3.2:1b → qwen3:4b）后，LR 模型的特征分布完全变了，必须重训 `scripts/train_lr_local.py`。

### 14. Ollama blob hash 会变
永远不要硬编码 Ollama 模型路径。用 `_resolve_ollama_blob()`（调用 `ollama show --modelfile`）动态解析。Ollama 更新后 hash 就变了。

### 15. 对抗训练数据比例极其敏感
v5 用 1:1 的 human:adversarial 导致模型把流畅人类文本当 AI 伪装 → 假阳性灾难。v6 改为 6:1。对抗样本是调料不是主菜。

### 16. AI 训练数据只用一个模型 = 单模型探测器
只用 DeepSeek 生成的 AI 文本训练，检测器只会认 DeepSeek 的指纹，对 GPT-4o/Claude/Gemini 可能失效。

### 17. XGBoost 不能在 DeBERTa 训练集上验证
这是数据泄露（循环泡沫）。94.6% OOD 准确率可能虚高。重训时必须用完全独立的数据。

### 18. dataset_merged_noised.jsonl 已损坏
10% 的词被替换为随机字符串。不要用于训练。只有 dataset_v4.jsonl 是干净平衡的。

### 19. Log-rank 信号在小模型上无用
llama3.2:1b 的 mean log-rank 无法区分 AI 和人类（~1.04 vs ~1.05）。需要 ≥8B 模型才有用。

### 20. CoPA 对抗解码骗不了 DeBERTa
0/6 通过率。只改变表面统计量，深层分类器照抓不误。正确方向是 StealthRL（GRPO LoRA）。

### 21. FAISS 要用 Python 3.11
FAISS 在 Python 3.12+ 有兼容问题。FAISS index + sentences.jsonl 共 9GB+，不适合 serverless，需要持久磁盘。

### 22. 没有 PPL 模型时检测严重退化
无 PPL 时融合退化为 DeBERTa-only，跨域 AUROC 0.5-0.6。服务器启动时应检查 PPL 可用性并警告。

### 23. tokenizer.vocab_size != model vocab
Qwen3.5 tokenizer 报 248044 但模型实际 248320。用 `model(mx.array([[1]])).shape[-1]` 取真实值。

---

## 四、CourseHub

### 24. Vercel 60 秒超时
AI 生成类 API 必须控制批次大小（如 generate-questions 每次最多 5 个 KP）。超过就 504。

### 25. localStorage 数据换设备丢失
打卡、学习时间、复习卡片状态存 localStorage。SRS 数据迁移到 Supabase 是待办（post-exam）。

### 26. Web Speech API 仅 Chrome/Edge
VoiceNotesPanel 在 Safari/Firefox 上不完全支持。

---

## 五、通用技术

### 27. llama-cpp-python 在 Apple Silicon 上编译不稳定
Metal 加速编译偶尔失败。遇到时清理 build cache 重装。

### 28. Tiptap v3 API 不稳定
Plugin API 还在演进，自定义 extensions 随时可能需要更新。

---

## 六、AI 助手执行层面（Claude 自身的坑）

### 29. 听不懂模糊指代就去硬搜
用户说的关键词不一定是项目名或文件名。先理解意图再搜索，不要拿关键词直接 grep 然后跑偏 2 个 turn。

**代价**：2026-04-09，用户说"experience"，我搜项目目录、搜组件名、搜错题本，浪费 2 轮才明白是"踩坑文档"。

### 30. 新对话忘记执行强制前置任务
CLAUDE.md 里写了"先建 Cron 再回复"，但每次新 session 都直接跳过。规则写了不等于会执行——需要 hook 或检查机制兜底。

**代价**：用户在 SessionStart hook 里专门加了提醒，说明之前每次都忘。

### 31. 编年记录不写或延后补写
每个 turn 结束必须写 chronicle，但经常忘记或打算"最后一起补"。

**代价**：用户多次提醒，已经存进 memory 作为最高优先级反馈。

### 32. 审查停在代码层，不质疑数据和假设
找 bug、检查文件是否存在、跑测试——这些是表面功夫。真正的审查是问"训练数据能覆盖真实场景吗""这个假设在生产中成立吗"。

**代价**：2026-04-06，用户 8 个问题 5 分钟找到了我几天没发现的盲区。

### 33. 反复请示技术决策打断用户
遇到技术分支时应该自己选最优方案执行，不要抛给用户。只在需要密码/付款/设计方向时才联系。

**代价**：用户被打断休息，明确发火。

---

## 如何维护这份文档

1. **踩到新坑 → 立即追加**，不要等到"有空再写"
2. **每条包含**：坑是什么、代价是什么（时间/金钱/数据丢失）、怎么避免
3. **已修复的坑**：加 ~~删除线~~ 但保留（历史参考），或移到底部"已解决"区
4. **季度清理**：删掉不再相关的条目（比如弃用的项目）
