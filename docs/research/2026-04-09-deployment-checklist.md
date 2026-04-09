# CourseHub — Vercel 部署完整清单

> 生成时间: 2026-04-09  
> 基于: 当日 Research Loop + Progress Loop 安全审计产出

---

## 前置条件（必须完成，否则部署失败）

### 1. Vercel Pro Plan 升级

所有 AI 路由均设置 `maxDuration = 60`。Hobby plan 函数超时上限 **10 秒**，AI 功能全部失效。

→ 升级到 Pro（$20/月）再部署。

---

### 2. 环境变量（Vercel Dashboard → Settings → Environment Variables）

| 变量 | 必须 | 来源 | 备注 |
|------|------|------|------|
| `NEXT_PUBLIC_SUPABASE_URL` | ✅ | Supabase 项目设置 | Public，设 Production + Preview |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | ✅ | Supabase 项目设置 | Public，设 Production + Preview |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | Supabase 项目设置 → Service Role | **Sensitive**，仅设 Production |
| `DASHSCOPE_API_KEY` | ✅ | 阿里云 DashScope 控制台 | **Sensitive**，仅设 Production |
| `UPSTASH_REDIS_REST_URL` | ✅（生产限流）| upstash.com → Redis 数据库 → REST API | 没有则限流降级为 in-memory（多实例失效） |
| `UPSTASH_REDIS_REST_TOKEN` | ✅（生产限流）| 同上 | 同上 |

**Upstash 免费注册步骤**（5 分钟）：
1. 访问 [upstash.com](https://upstash.com) → Create Database → 选 Region: **ap-northeast-1（东京）**（与 Vercel hnd1 同区，延迟最低）
2. 数据库创建后 → REST API → 复制 URL 和 Token
3. 填入 Vercel 环境变量

---

### 3. Supabase Auth 配置

在 Supabase 控制台 → Authentication → URL Configuration：

- **Site URL**: `https://your-domain.vercel.app`
- **Additional Redirect URLs**: `https://*.vercel.app/**`（覆盖所有 Preview 部署）

不配置 → Google OAuth 回调失败（401 错误）。

---

## 部署后验证（按顺序）

### Step 1: 基础连通性
```
✅ 访问 https://your-domain.vercel.app → 页面加载
✅ 控制台无 CORS 报错
✅ Supabase 连接正常（登录页可渲染）
```

### Step 2: 认证流程
```
✅ 邮箱注册 → 收到确认邮件
✅ 邮箱登录 → 成功跳转
✅ Google OAuth → 回调正常（不 401）
```

### Step 3: 核心 AI 功能（各测试一次）
```
✅ 上传 Syllabus PDF → AI 解析大纲（测试 parse + generate）
✅ 聊天功能 → 发送消息收到回复（测试 chat）
✅ 生成练习题 → 出题成功（测试 generate-questions）
✅ 生成课程章节 → 章节内容生成（测试 lessons/generate-one）
```

### Step 4: Rate Limit 验证
```
✅ 快速点击生成按钮 6 次 → 第 6 次应看到 429 错误提示
✅ 等 60 秒后再次尝试 → 成功（确认 Upstash 限流有效）
```

### Step 5: 检查 Vercel 日志
```
✅ Vercel Dashboard → Deployments → 最新部署 → Functions
✅ 无 500 错误
✅ AI 函数执行时间 < 60s
```

---

## 代码层面已就绪（本日自动完成）

| 修复 | Commit |
|------|--------|
| P0: rate-limit in-memory → Upstash Redis（graceful fallback）| `07ff87f` |
| P1: rate-limit 按 config 缓存（chat/generate 阈值修正）| `419c721` |
| P1: x-forwarded-for 可伪造 → user.id | `fc5b8d6` |
| P1: generate key DoS 漏洞（缺少 user.id）| `51d0a02` |
| P1: exam-prep, generate-questions, generate-one 添加限流 | `36ff91f` |
| P1: exam-scope, lessons, notes/organize, regenerate, extract 添加限流 | `5db1047` |
| P1: fork 添加限流 | 当前 commit |
| P1: vercel.json 添加 hnd1 区域（DashScope 延迟 10x 改善）| `07ff87f` |
| P2: AbortSignal.timeout → SDK 原生 timeout 参数 | `2484f13` |

---

## 可选优化（上线后再做）

### Qwen3.5-plus 禁用思维链（节省 ~30% token）

**本地测试后**实施（详见 `docs/research/2026-04-09-ai-sdk-timeout-thinking-mode.md`）：

```ts
// src/lib/ai.ts — 为 textModel 单独创建 provider
const qwenText = createOpenAI({
  baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1",
  apiKey: process.env.DASHSCOPE_API_KEY ?? "",
  fetch: async (url, init) => {
    if (init?.body && typeof init.body === "string") {
      const body = JSON.parse(init.body);
      body.enable_thinking = false;
      return fetch(url, { ...init, body: JSON.stringify(body) });
    }
    return fetch(url, init);
  },
});
const textModel = qwenText("qwen3.5-plus");
```

测试要点：
1. 确认输出不含 `<think>` 块
2. JSON 解析结果与 thinking 模式一致
3. 延迟应减少 1-3s
