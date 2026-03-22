# AI Text X-Ray — 项目状态

> 最后更新: 2026-03-21 23:30

---

## 最近更新（新的在上面）

### [2026-03-21 23:30] — Landing Page 重做 + 字体修复

- **做了什么**：重写产品首页为 premium landing page。Hero 区有 X-Ray 扫描动画（文字逐词变色显示 AI 概率）。工具卡片、How It Works 深色区、数字滚动动画、差异化区、CTA。工具界面从 `/` 移到 `/app`。移除 Instrument Serif（用户不喜欢），改用 Geist Sans 300。
- **架构决策**：`/` = 静态 landing（SSR，SEO 友好），`/app` = client-side 工具（AppShell）。用 `Instrument_Serif` 做 display font 被否决，教训：字体选择必须先调研 3+ 个参考产品。
- **踩过的坑**：Instrument Serif 太粗。端口 3000 被其他项目占用，ai-text-detector 在 3003。
- **当前状态**：Landing page 可用 http://localhost:3003。
- **下一步**：Learn 页面、更多 Blog、credibility 数据。字体暂用 Geist Sans，定制字体搁置。

### [2026-03-21 22:00] — Writing Center 对话式 Onboarding

- **做了什么**：重写 WritingCenter.tsx，三阶段状态机 `welcome → conversation → writing`。Welcome = starter 卡片页（类似 claude.ai）；Conversation = 纯 AI 对话（无编辑器）；Writing = 完整编辑器 + 协作面板。
- **架构决策**：`phase` state 控制视图切换。有已保存 draft 的用户直接跳 writing phase。
- **踩过的坑**：最初设计平铺所有功能导致信息过载。参考 claude.ai 后改为渐进展开。
- **当前状态**：代码完成，未做完整 smoke test。
- **下一步**：用户描述了更深的流程（AI 搜索研究 → brainstorm → AI 生成草稿），需要 web search API。

### [2026-03-21 20:00] — Writing Center MVP-1 全部组件完成

- **做了什么**：
  - Phase 0: 12 篇测试文章 + 7 个 role prompts + 35 daily tips + 10 lab examples
  - Prompt calibration: 2 轮，88.9% 通过率（128/144）
  - Phase 1: `/api/writing-assist` route（7 actions, DeepSeek V3）
  - Phase 2: Tiptap Editor + ChatPanel + 4 子组件 + 全部 AI 联动 + 双向 annotation 链接 + streak
  - Phase 3: LabPanel + 集成
- **架构决策**：
  - DeepSeek V3 替代 Claude API（成本低 10-35x）
  - Temperature 按 action 分层：analyze=0, dialogue=0.7, lab-rewrite=per-request
  - Tiptap inline Decoration（不是 gutter，gutter 太复杂留 Phase 2）
  - localStorage 全部状态（兼容 MVP-2 Supabase 迁移）
  - Liz Lerman 顺序：good → question → suggestion → issue
  - Conventions 压制：Ideas/Organization 有 issue 时不显示语法批注
  - SRSD 脚手架递减：genreExperience 每 session 只 +1
- **踩过的坑**：
  1. Tiptap + Next.js：必须 `immediatelyRender: false`
  2. DeepSeek temperature 映射：API temp × 0.3 = 实际 temp
  3. Calibration 第一轮 79.9%：good annotations 不引用原文 → 加 WRONG/RIGHT 示例；分数波动 → 取整到 5 + 放宽 ±10；Conventions 压制不一致 → 显式 4 步流程
  4. `@anthropic-ai/sdk` 装了没用（改用 `openai` 包调 DeepSeek）
  5. 多 subagent 并行改同一文件会覆盖
- **当前状态**：build 通过，未 smoke test。
- **下一步**：浏览器完整走一遍流程修 bug。

### [2026-03-21 04:00] — 50M 语料库构建完成

- **做了什么**：Colab A100 构建 50M 句子语料库，FAISS IVF+PQ 索引。chunk-streaming 构建（不用 memmap）。SentenceStore 字节偏移索引（400MB 内存 vs 8GB）。
- **数据源配置**：C4 30% (28M) / Wikipedia 20% (2.8M，不够 10M 目标，C4 backfill 补) / CC-News 20% (5.3M, 排除 2019+ 防 AI 污染) / CNN-DailyMail 15% (5.7M) / Gutenberg 15% (7.5M)。全部 pre-2019 无 AI 污染。
- **构建脚本**：`scripts/build_corpus_colab.py`。CRC32 双哈希去重。每 1M 句子一个 chunk（.npy + .jsonl）。崩溃恢复靠 hash 集重建。
- **humanizer 内存优化**：`SentenceStore` 类（humanizer.py:35-83），用 numpy 偏移数组替代 Python list。首次启动扫描 JSONL 建偏移索引缓存为 `.offsets.npy`（~381MB），后续秒加载。单文件句柄不是线程安全——当前单线程 HTTP server 无影响。
- **踩过的坑**（13 个，按时间顺序）：
  1. `torch.cuda.get_device_properties(0).total_mem` → 改 `.total_memory`
  2. faiss pip install 被注释 → 改 `subprocess.check_call` 自动安装
  3. CUDA 12.8 需要 `faiss-gpu-cu12`（不是 `faiss-gpu`）
  4. BookCorpus `trust_remote_code` 废弃 → 换 C4
  5. BookCorpus `Dataset scripts no longer supported` → 同上
  6. PubMed 嵌套字典取值脆弱 → 换 CNN/DailyMail
  7. 30M→50M 后 `np.concatenate` 72GB 峰值 → 改 memmap（后又改为 chunk-streaming）
  8. 崩溃恢复 `skip_remaining` 逻辑 bug → 删 skip 逻辑，纯靠 hash 去重
  9. MD5 hash 性能 → 改 CRC32 双哈希
  10. memmap 训练采样随机 I/O 极慢 → `np.sort()` 排序后顺序读
  11. C4 backfill 无限循环 → `backfill_failures` 计数器，3 次后终止
  12. Colab 断连丢 chunk → 改挂载 Google Drive
  13. memmap 写 Drive FUSE → FileNotFoundError → 改 chunk-streaming（不用 memmap）
  14. Colab 磁盘满 → DriveFS lost_and_found 缓存 144GB，手动清理
  15. faiss-gpu 安装后 `get_num_gpus()=0` → 需重启 runtime（C 扩展缓存）
- **当前状态**：`corpus/sentences.faiss` (2.7GB) + `sentences.jsonl` (6.2GB) 已部署。humanizer.py 加载正常（50M 条目，381MB 偏移索引）。
- **下一步**：不需要再动。如需重建：Colab 脚本在 Google Drive `/content/drive/MyDrive/corpus_build/` 有原始数据。

---

## 当前状态：数据集重建中

DeBERTa 分类器尚未可用。训练管线已修复，等待数据集重建后重新训练。

## 阻塞项

### 数据集质量缺陷（正在修复）
`generate_dataset.py` 的 `load_human_texts` 将语料库句子随机打乱后拼接，导致 human 样本（label=0）不连贯——法语翻译混八卦、体育混政策。模型学到"连贯=AI，不连贯=human"，在真实文本上完全失效。

**已修复代码**：`load_human_texts` 改为连续窗口采样，保持文章内连贯性。

**待执行**：用修复后的函数重新生成 human（17,500 条）和 human_polished（17,500 条），保留 ai + ai_polished（35,000 条），重建 `dataset.jsonl`。

### 训练管线缺陷（已修复）
1. **DeBERTa gamma/beta bug**：`load_best_model_at_end=True` 加载 checkpoint 时 LayerNorm 命名不匹配（`.gamma/.beta` vs `.weight/.bias`），静默丢失所有 LayerNorm 权重。**修复**：`load_best_model_at_end=False`，`save_strategy='no'`。
2. **权重丢失**：cell-6 可被重跑覆盖 model 变量，cell-10 保存 base 权重。**修复**：训练完成后在同一 cell 立刻自动保存 + 验证 classifier std。

## 各模块状态

| 模块 | 状态 | 说明 |
|------|------|------|
| 前端 UI | ✅ 可用 | 检测/改写/写作三面板，GPTZero 风格可视化已加 |
| Python 检测后端 | ✅ 代码就绪 | llama.cpp token 分析 + DeBERTa 推理，等模型权重 |
| Python 改写后端 | ✅ 可用 | 7 种 FAISS 语义改写方法 |
| 50M 句子语料库 | ✅ 完成 | FAISS IVF+PQ 索引 2.6GB |
| 70K 训练数据集 | ❌ 需重建 | human + human_polished 不连贯，需重新生成 |
| DeBERTa 分类器 | ❌ 不可用 | 本地 models/detector/ 存的是 base 权重 |
| Colab 训练 notebook | ✅ 已修复 | gamma/beta bug + 自动保存 + 验证 |
| 部署 | ❌ 无 | 无 Docker/Vercel 配置 |

## 下一步（按顺序）

1. 重建数据集：重新生成 human + human_polished（用 DeepSeek + Qwen API）
2. 上传到 Google Drive，Colab 训练 DeBERTa（~30 分钟 A100）
3. 下载训练好的模型到 models/detector/，验证可用
4. 实现 X-Ray Vision（token 级热力图）— 核心差异化功能
5. 部署方案

## 技术栈
Next.js 16 + TypeScript + Tailwind 4 + Recharts — Python: DeBERTa + llama.cpp + FAISS + spaCy

## 快速上手
```bash
npm install && npm run dev          # 前端 → localhost:3000
ollama pull llama3.2:1b
python3 scripts/perplexity.py       # 检测后端 → localhost:5001
python3 scripts/humanizer.py        # 改写后端 → localhost:5002
```

## 关键决策记录

| 日期 | 决策 | 原因 |
|------|------|------|
| 2026-03-21 | 关闭 load_best_model_at_end | DeBERTa-v3 gamma/beta 命名 bug 导致 checkpoint 加载静默损坏模型 |
| 2026-03-21 | human 文本改用连续窗口采样 | 随机拼接导致模型学习"连贯性"而非"AI 特征" |
| 2026-03-21 | 训练后同 cell 自动保存 + 验证 | 防止 cell-6 重跑覆盖训练结果 |

## 已知问题
- `.env.local` 含真实 API key，上线前必须轮换
- Git remote URL 中嵌了 GitHub token
- 10k 字符限制对长文检测是瓶颈
- 项目总体积 ~14GB（语料库 + 模型）
