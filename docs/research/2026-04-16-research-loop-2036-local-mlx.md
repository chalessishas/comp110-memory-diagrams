# Research Loop 20:36 — 本地 MLX 替代 OpenAI API 方案

生成时间：2026-04-16 23:00（首次派 Agent 462s 超时，改为 parent 自行 WebSearch × 2.5）
前置：[Turn 17 OpenAI API 方案](2026-04-16-research-loop-1900.md)

---

## 1. 研究方向和动机

Turn 17 方案需要引入 Vercel Serverless proxy + API key 管理 + opt-in 隐私 flow，**首次破坏 TOEFL 项目"纯前端无后端"承诺**。主人本机有 Python 3.13 + MLX 环境（见 `~/.claude/CLAUDE.md` Python Environment 段），因此有**不跨越承诺**的替代：让主人本机跑 `mlx_lm.server` 作为本地 OpenAI 兼容 endpoint，TOEFL 前端 `fetch('http://localhost:8080/...')` 连接。本次研究回答：这条路径 2025-2026 是否已成熟。

---

## 2. 外部证据

### E1. mlx-lm 官方提供 OpenAI 兼容 HTTP API
`ml-explore/mlx-lm` 仓库 `mlx_lm/SERVER.md` 记录了内置 server，命令 `mlx_lm.server --model <hf-id> --port 8080` 即起。API 结构与 OpenAI chat/completions 一致。

URL: https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/SERVER.md

### E2. 第三方包生态成熟（2025-2026）
- **vllm-mlx**（2026）：Apple Silicon 原生 vLLM，**400+ tok/s**，支持 continuous batching + MCP tool calling，OpenAI + Anthropic 兼容 — https://github.com/waybarrios/vllm-mlx
- **mlx-openai-server**（PyPI / cubist38）：FastAPI 架构，同时支持 vision + language 模型 — https://github.com/cubist38/mlx-openai-server
- **FastMLX**：轻量 OpenAI 兼容 wrapper — https://blaizzy.github.io/fastmlx/

### E3. Ollama 官方换用 MLX 后端（2026 preview）
Apple 官方背书的信号：Ollama 在 Apple Silicon 上已切到 MLX，意味着"本地 LLM"生态往 MLX 收敛。

URL: https://ollama.com/blog/mlx

### E4. 小模型 4-bit 推理速度（M-series 2025-2026 基准）
- **Qwen3.5-9B MLX**: 73 tok/s（M-series 2025 优化版 2× 基线）— https://dev.to/thefalkonguy/installing-qwen-35-on-apple-silicon-using-mlx-for-2x-performance-37ma
- **7B 优化模型**：~230 tok/s 峰值（MLX benchmarks）
- **14B 量化模型 M2/M3 Max**：25-40 tok/s
- **Phi-3.5 Mini 3.8B 4-bit 推算**：50-100 tok/s
- MLX 比 llama.cpp 快 20-50%（<14B 模型甚至 20-87%）

### E5. Turn 17 引用仍然适用
TOEFL11 上 rubric-based 评分 QWK 提升 +0.19（arxiv 2510.09030, 2025-10），简化 rubric 精度与完整相当（arxiv 2505.01035, 2025-05）。但这些实验用的是 GPT-4.1 / Gemini-2.5-Pro / Qwen-3-Next-80B 级别模型。**小模型（3-4B）QWK 提升预估在 +0.10**（没有直接 benchmark，外推自小-大模型一般的 70% effective 规律）。

---

## 3. 本地 MLX 方案具体形态

### 3.1 模型选型
**首选 Phi-3.5 Mini 3.8B instruct（4-bit 量化）**：
- 内存 ~2.5GB（M-series 16GB+ 无压力）
- 延迟：250 prompt + 80 output tokens × 100 tok/s ≈ **3.3s**（和 OpenAI API 2-4s 相当）
- HF: `mlx-community/Phi-3.5-mini-instruct-4bit`

备选 Qwen3-4B 或 Llama-3.2-3B-instruct — 取决于哪个在简化 rubric prompt 下表现最稳。

### 3.2 启动命令（主人手动）
```bash
/opt/anaconda3/bin/python3.13 -m mlx_lm.server \
  --model mlx-community/Phi-3.5-mini-instruct-4bit \
  --port 8080
```
主人自用时运行，关掉终端就停。**无守护进程、无 launchd、无自动启动** — 保持"主人在场才可用"的属性，和 TOEFL 自用定位天然契合。

### 3.3 TOEFL 前端接入（最小改动）
新增 `src/writing/scorer/llmScorer.js`：
```js
export async function score(text, taskType, promptText) {
  try {
    const r = await fetch('http://localhost:8080/v1/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: 'local', messages: [...], temperature: 0 }),
      signal: AbortSignal.timeout(8000),
    })
    if (!r.ok) return null  // server not running → graceful null
    // parse 3-trait rubric JSON → return { value: 0..1, details, rationale }
  } catch {
    return null  // network error / CORS / timeout
  }
}
```
在 `scorer/index.js` 聚合时：`if (llmResult) weighted average else 跳过 llm 维度` — 保持向后兼容。

### 3.4 降级策略
- **主人 mlx_lm.server 未开**：fetch 失败 → llmScorer 返回 null → index.js 按 7 模块（原样）评分
- **其他人访问 hdmap-style 部署（未来如果有）**：localhost:8080 不可达 → 同上降级
- **CORS**：mlx_lm.server 默认允许同源，如果 Vite dev 在 :5173，需要 server 加 `--cors-allow "*"` 或主人改走 dev proxy

---

## 4. 对比决策矩阵

| 维度 | Turn 17 OpenAI API | 本次本地 MLX | 权重 |
|-----|---------------------|-------------|-----|
| 纯前端承诺 | ❌ 需 edge proxy | ✅ 不破坏 | 高（主人项目身份认同）|
| 主人钱包 | ~$6/月 @ 500 DAU | $0 | 中 |
| 启动门槛 | 配 Vercel env + deploy | `mlx_lm.server` 单行命令 | 高 |
| 延迟 | 2-4s（网络 RT） | ~3.3s（本地推理） | 中 |
| QWK 提升 | +0.19（实证） | +0.10（推算） | 高 |
| 隐私 | 数据出 OpenAI | 不出本机 | 高 |
| 可部署给他人 | ✅ 任何访问 hdmap 的用户 | ❌ 只主人本机可用 | **关键** |
| 设备限制 | 任何联网设备 | 必须 Apple Silicon + MLX | 低（主人本机即可）|
| API key 泄露风险 | 有（需 proxy） | 无 | 高 |

**综合**：TOEFL 项目今天的实际使用场景是**主人自用**（CLAUDE.md 没列上线计划，不像 Signal-Map 那样已部署 hdmap.live）。"可部署给他人" 列对自用场景几乎零权重，本地 MLX 在其他所有维度优势明显。

---

## 5. 推荐路径

### 路径 C（双模式，最优）
- **主人自用**：本地 MLX 方案。`mlx_lm.server` 起 → TOEFL 前端 fetch localhost → 有 LLM 加成
- **其他场景**：llmScorer 返回 null → 自动降级到 7 模块规则评分（当前 10/10 校准，仍然能用）
- **代码只有一份**：`llmScorer.js` 有 graceful null，scorer/index.js 一处 if-else 聚合，**不需要条件编译、不需要环境分支**

### 为什么不选纯路径 A（Turn 17 OpenAI）
- 破坏"纯前端无后端"承诺换来 +0.09 额外 QWK（0.19 vs 0.10）对自用场景不值
- $6/月不高但是未来隐私合规会拖 iteration 速度

### 为什么不选纯路径 B（纯本地 MLX）
- 没意义——本地 MLX 本来就是 graceful null 自动降级，不需要"纯"

### 如果主人真的想让 TOEFL 变公开产品
再回到 Turn 17 的 OpenAI 方案，路径 C 当前不阻塞未来切换。

---

## 6. 下一步命令

1. **（主人手动，一次性，~5 分钟）**：首次下载 Phi-3.5 Mini 4-bit
   ```bash
   /opt/anaconda3/bin/python3.13 -c "from mlx_lm import load; load('mlx-community/Phi-3.5-mini-instruct-4bit')"
   ```
2. **（主人手动，每次使用前）**：启动 server
   ```bash
   /opt/anaconda3/bin/python3.13 -m mlx_lm.server \
     --model mlx-community/Phi-3.5-mini-instruct-4bit \
     --port 8080 --cors-allow "*"
   ```
3. **（agent 可自主，~60 行）**：写 `src/writing/scorer/llmScorer.js` stub，不接入 index.js 聚合，仅作为独立模块。**本 Progress Loop 立即交付**。
4. **（两周观察）**：主人手动跑几篇 essay，记录 "规则 overall" vs "规则+MLX overall" 的差异，如果系统性提高 S4→S5 区分 → 接入 index.js 聚合加权。如果看不出差异 → 不接入，保留 stub 供未来替换模型。

---

## Sources

- [mlx-lm SERVER.md (ml-explore)](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/SERVER.md)
- [vllm-mlx (waybarrios)](https://github.com/waybarrios/vllm-mlx)
- [mlx-openai-server (cubist38)](https://github.com/cubist38/mlx-openai-server)
- [FastMLX](https://blaizzy.github.io/fastmlx/)
- [Ollama + MLX (2026)](https://ollama.com/blog/mlx)
- [Qwen 3.5 MLX 2× perf (2025)](https://dev.to/thefalkonguy/installing-qwen-35-on-apple-silicon-using-mlx-for-2x-performance-37ma)
- Turn 17 报告的 arxiv 引用仍适用：arxiv 2510.09030, 2505.01035
