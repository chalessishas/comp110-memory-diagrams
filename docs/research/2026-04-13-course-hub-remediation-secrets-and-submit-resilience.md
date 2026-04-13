# course-hub 修复剧本：密钥卫生 + QuestionCard 失败分支

**日期**：2026-04-13
**范围**：只读审查 `course-hub/`（隶属 `VScode Workspace` monorepo，remote 为 `github.com/chalessishas/T-DBDD.git`），不做任何代码修改；剧本面向主会话 / 主人本人执行。
**选中题目**：
1. 🔴 P0 — `.env.local` 中的 `SUPABASE_SERVICE_ROLE_KEY` + `DASHSCOPE_API_KEY` 卫生加固 + 预防性轮换
2. 🟠 P1 — `QuestionCard.tsx:50-75` submit 无失败分支导致题卡假死

其他 5 项暂不纳入本剧本；P0/P1 杠杆最高且互不冲突，可一个下午做完。

---

## 一、先纠正一个事实判定

主会话两轮审查说"`.env.local` 已进 git history"。**这个结论是错的**，本次做了如下取证：

```
# 在 workspace 根（course-hub 是子目录，没独立 .git）
git log --all --full-history -- course-hub/.env.local course-hub/.env .env.local .env
# → 空输出（从未 track 过）

git rev-list --all | xargs -I{} git ls-tree -r {} | grep -E "\.env(\.local)?$"
# → 空输出（所有 tree 里都不存在）

git log --all -p | grep -cE "eyJ[A-Za-z0-9_-]{20,}"
# → 1 条命中，但检查该行是 package-lock.json 的 integrity sha512 base64，不是 JWT

git log --all -p | grep -cE "sk-[A-Za-z0-9]{20,}"
# → 0
```

`.gitignore` 首行起就是 `.env*`。**未发生 GitHub 外泄**。

这不代表 P0 不做，而是：威胁模型从"公网已泄露，必须 6 小时内轮换+清 history"降级为"本地明文密钥 + 多代理/日志/崩溃报告/截图可能接触过 + 长期未轮换"。应对仍然要做，但优先级排在 P1 生产 bug 之后也合理——下面按"先修 P1（用户今天就会撞的 bug）→ 再做 P0 预防性加固"的顺序给剧本。

---

## 二、P1 剧本：QuestionCard submit 加失败分支

### 问题定性

`course-hub/src/components/QuestionCard.tsx:50-75` 的 `handleSubmit`：

```tsx
async function handleSubmit() {
  if (!userAnswer || submitting) return;
  setSubmitting(true);
  const res = await fetch("/api/attempts", { … });
  const data = await res.json();   // ← 非 JSON 会 throw，无 catch
  const correct = data.is_correct ?? false;   // ← 500 + HTML 错误页时 data 可能是 {error:...}，correct=false
  …
  setSubmitted(true);              // 只有 happy path 才会走到
}
```

### 量化影响

- **Vercel serverless 冷启动 / 60s timeout**：course-hub 的 API 已知在 AI 类端点容易 timeout，fetch 会 reject → throw → 未被捕获 → Promise unhandled → `submitting` 永远 `true` → 用户看到 Loader 转圈永不停 → 唯一出路是刷新整页丢失答案。
- **rate limit / Supabase 闪断**：返回 JSON `{error:"..."}`，`data.is_correct` 为 undefined，题卡判成错题写入 FSRS（`Rating.Again`），污染复习调度。
- **假设日 active user 20、日答题 300**，即使 1% 失败率就是 **每天 3 次题卡卡死 + 3 次错误 FSRS 扣分**。

### 执行前只读验证

在主会话或主人终端跑（只读）：

```bash
cd "/Users/shaoq/Desktop/VScode Workspace/course-hub"
# 看 /api/attempts 路由是否返回标准 { is_correct, correct_answer, explanation } 结构
grep -n "export async function POST" src/app/api/attempts/route.ts
grep -nE "return.*NextResponse|return.*Response" src/app/api/attempts/route.ts
```

### 修复补丁（给主会话 Edit 用，这里只描述、不执行）

**目标文件**：`course-hub/src/components/QuestionCard.tsx`
**替换范围**：第 50-75 行 `async function handleSubmit()` 整个函数体

**新实现骨架**（最小改动，保持 API 签名不变）：

```tsx
async function handleSubmit() {
  if (!userAnswer || submitting) return;
  setSubmitting(true);
  try {
    const res = await fetch("/api/attempts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question_id: question.id, user_answer: userAnswer, confidence }),
    });
    if (!res.ok) {
      // 非 2xx：不污染 FSRS，不 setSubmitted，允许用户重试
      const msg = await res.text().catch(() => "");
      console.error(`[attempts] ${res.status}`, msg);
      // TODO(i18n): 用 toast 反馈；此处先用 alert 避免静默失败
      alert(t("questionCard.submitFailed") ?? "Submit failed, please retry.");
      return; // finally 会把 submitting 归位
    }
    const data = await res.json();
    const correct = data.is_correct ?? false;
    setIsCorrect(correct);
    setRevealedAnswer(data.correct_answer ?? null);
    setRevealedExplanation(data.explanation ?? null);
    setExplanationVisible(correct);
    setSubmitted(true);
    updateCard(question.id, correct ? Rating.Good : Rating.Again);
    recordActivity("question");
    onAnswer(question.id, userAnswer, correct);
  } catch (err) {
    console.error("[attempts] network error", err);
    alert(t("questionCard.submitFailed") ?? "Network error, please retry.");
  } finally {
    setSubmitting(false); // 关键：成功也 reset，避免和 setSubmitted 并存下按钮状态错乱
  }
}
```

**关键点**：
1. `res.ok` 拦非 2xx，避免把 500 的 HTML/错误 JSON 喂给 FSRS。
2. `try/catch/finally` 包裹，`setSubmitting(false)` 放 finally 保证任何路径都 reset。
3. 失败不 `setSubmitted(true)`，用户保留重试机会。
4. `alert` 是过渡实现；如果项目已有 toast 组件（检查 `src/components/ui/`）应替换。

### 验证

```bash
# 1) 类型检查（只读 = 不改代码也能验证当前 baseline）
cd "/Users/shaoq/Desktop/VScode Workspace/course-hub" && npx tsc --noEmit

# 2) 修复后手工复现
# 在 dev server 里故意把 /api/attempts 改 500 或断网，点 Submit
# 期望：alert 弹出 + 按钮恢复可点 + 可再次提交
```

### 耗时 / 风险 / 回滚

- **耗时**：改代码 10 分钟，手工测 5 分钟。
- **风险**：`alert` 在 PWA / 生产环境丑，但比"永远 loading"好 100 倍；可在下一轮换 toast。
- **回滚**：`git revert <commit>` 即可，本函数纯客户端逻辑，无数据库迁移。

---

## 三、P0 剧本：密钥卫生 + 预防性轮换

### 问题定性

- `course-hub/.env.local`（4 行）含 `SUPABASE_SERVICE_ROLE_KEY`（legacy `service_role` JWT，**绕过所有 RLS**）和 `DASHSCOPE_API_KEY`（Alibaba Cloud，按 token 扣费）。
- 未进 git，但：
  - 过去 10 天多代理会话频繁读项目，密钥**可能出现在 AI context / 崩溃栈 / Vercel build log / 截图**。
  - 从未轮换过（文件 mtime `Apr 3 20:11`，存活 10 天）。
  - 没有 pre-commit scanner，未来任何 `git add .` + 一次 .gitignore 写错就能泄出去。

### 威胁面量化

| 资产 | 泄露后损失 |
|---|---|
| Supabase `service_role` | 绕过 RLS → 读/写/删任意 user 的 course/attempt/upload；删 auth.users 导致全部用户登录失败 |
| DashScope key | 按 token 付费；Qwen3.5-Plus 一次恶意脚本可跑出数百到数千元账单；Alibaba 无自动封顶（需手动设配额） |
| Supabase `anon` | 低危（配合 RLS 即公开值），但建议同期迁移到新 `sb_publishable_...` |

### 剧本 A — 预防性加固（必做，30 分钟）

#### A.1 彻底确认未泄露（已在本文件顶部完成，5 个命令全绿）

```bash
cd "/Users/shaoq/Desktop/VScode Workspace"
git log --all --full-history -- course-hub/.env.local course-hub/.env .env.local .env
git rev-list --all | xargs -I{} git ls-tree -r {} | grep -E "\.env(\.local)?$"
git log --all -p | grep -cE "sk-[A-Za-z0-9]{20,}"   # 期望 0
git log --all -p | grep -cE "eyJ[A-Za-z0-9_-]{60,}" # 期望 0-1，>1 就要 review
```

#### A.2 安装 Gitleaks pre-commit（Gitleaks 为 2026 公认的速度最优、150+ 规则的 pre-commit 选型，TruffleHog 做 CI 补位）

```bash
# macOS
brew install gitleaks pre-commit

# 在 workspace 根创建 .pre-commit-config.yaml（已有则 merge）
cat > "/Users/shaoq/Desktop/VScode Workspace/.pre-commit-config.yaml.new" <<'YAML'
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.2
    hooks:
      - id: gitleaks
YAML

# 如果已经有 .pre-commit-config.yaml，先 diff 再覆盖
diff "/Users/shaoq/Desktop/VScode Workspace/.pre-commit-config.yaml" \
     "/Users/shaoq/Desktop/VScode Workspace/.pre-commit-config.yaml.new" 2>/dev/null || \
  mv "/Users/shaoq/Desktop/VScode Workspace/.pre-commit-config.yaml.new" \
     "/Users/shaoq/Desktop/VScode Workspace/.pre-commit-config.yaml"

cd "/Users/shaoq/Desktop/VScode Workspace" && pre-commit install

# 验证：把一个假 key 写到 /tmp 再 git add 看是否被拦
echo 'SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiJ9.FAKE.FAKE' > /tmp/leak-test.txt
cp /tmp/leak-test.txt "/Users/shaoq/Desktop/VScode Workspace/leak-test.txt"
cd "/Users/shaoq/Desktop/VScode Workspace" && git add leak-test.txt && git commit -m "test" 2>&1 | head -20
# 期望：pre-commit 拒绝 + 标红该行。验证完：
git reset HEAD leak-test.txt && rm leak-test.txt
```

#### A.3 一次全 history 扫描（已干净，做个 baseline 留档）

```bash
cd "/Users/shaoq/Desktop/VScode Workspace"
gitleaks detect --source . --log-opts="--all" --report-path=/tmp/gitleaks-baseline.json
# 预期 findings = 0；如果 >0，跳到剧本 B
```

#### A.4 加固 .gitignore + 文档

只读提议（主会话来 Edit）：

```
# course-hub/.gitignore 底部追加（若未有）
.env*
.env.local
.env.*.local
!.env.example
!.env.local.example
```

### 剧本 B — 预防性轮换（强烈建议，45 分钟）

**为什么做**：即便未外泄，10 天未轮换 + service_role 可绕 RLS，成本极低且 Supabase 2026 已把 legacy 迁移 + 轮换合二为一。

#### B.1 Supabase：迁移到新 API keys 体系并轮换 service_role

参考 [Supabase Docs · Understanding API keys](https://supabase.com/docs/guides/api/api-keys) 和 [Rotating Anon, Service, and JWT Secrets](https://supabase.com/docs/guides/troubleshooting/rotating-anon-service-and-jwt-secrets-1Jq6yd)：

1. Dashboard → Project `zubvbcexqaiauyptsyby` → **Settings / API Keys** 页。
2. 若还在用 legacy `service_role`，**先创建新 `sb_secret_...`**（推荐迁移，legacy 将废弃）。**这一步新旧并存，零 downtime**。
3. 在 Vercel Project Settings → Environment Variables 把 `SUPABASE_SERVICE_ROLE_KEY` 替换为新值。所有环境（Production/Preview/Development）都要更新。
4. 本地同步：

```bash
# 只读查看当前值的前后 4 字符做 sanity check，不打全串
awk -F= '/SERVICE_ROLE/ {print substr($2,1,4)"..."substr($2,length($2)-3)}' \
  "/Users/shaoq/Desktop/VScode Workspace/course-hub/.env.local"
# 手工更新 .env.local 的 SUPABASE_SERVICE_ROLE_KEY=<new_sb_secret_...>
```

5. 在 Supabase Dashboard 观察 **"Last used"** 列，确认旧 key 30 分钟无活动后，**Deactivate** 旧 key。
6. （可选但推荐）在 JWT Signing Keys 页 **Rotate Keys**：会把当前 key 移到 "Previously used"，立刻签发新 JWT 仍会校验旧 key 一段时间以保持现有用户 session 可用。

#### B.2 DashScope 轮换

参考 [Alibaba Cloud Model Studio · How to get an API Key](https://www.alibabacloud.com/help/en/model-studio/get-api-key)：

1. 登录阿里云 Model Studio → API-KEY 管理页。
2. **Create API Key**（获得新值）→ 更新 Vercel + 本地 `.env.local`。
3. 把旧 key **Delete / Disable**。DashScope 当前 UI 没有独立 revoke，只能 Delete 或通过 RAM 禁用该 RAM user。
4. **立即在 Model Studio → Quota 页面设置配额上限**（每日 token 配额 + 欠费停机），DashScope **默认无自动封顶**——这是主人长期的潜在大坑。

#### B.3 轮换后验证

```bash
cd "/Users/shaoq/Desktop/VScode Workspace/course-hub"
# 本地 dev 重启
npm run dev
# 另起一个 terminal：触发一次需要 service_role 的 API（例如管理端课程清理）+ 一次需要 DashScope 的 API（例如 generate-questions）
# 看 console 无 401/403/AuthApiError
```

### 剧本 C — 如果剧本 A.3 发现 findings（当前不需要，留档）

2026 最佳实践共识：**BFG 做主流量、git-filter-repo 做精细场景**。单文件 / 单字符串清除用 BFG 更快（10-720x），跨仓库复杂重写用 filter-repo。

```bash
# 仅在 A.3 发现密钥时才跑，且执行前 git clone --mirror 一份裸仓库做备份
cd /tmp && git clone --mirror https://github.com/chalessishas/T-DBDD.git T-DBDD.git
cd T-DBDD.git

# 用 BFG 删除匹配文件（推荐）
brew install bfg
echo "SUPABASE_SERVICE_ROLE_KEY=*" > /tmp/secrets.txt
echo "DASHSCOPE_API_KEY=*" >> /tmp/secrets.txt
bfg --replace-text /tmp/secrets.txt
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push --force   # ← 协作者必须重新 clone；本仓库目前单人，OK
```

**风险**：force push 会让所有基于旧 history 的 PR/branch 变成 orphan；协作场景禁用。

### 耗时 / 回滚

- **A（加固）**：30 分钟，无回滚风险（pre-commit 出错可 `pre-commit uninstall`）。
- **B（轮换）**：45 分钟。回滚 = 把旧 key 重新 activate；在 Supabase 上 30 分钟内可恢复，DashScope delete 后不可恢复需重建（会丢 key ID，但项目里都是按环境变量引用无影响）。
- **C（清 history）**：45-90 分钟，force push 不可逆，必做 mirror 备份。

---

## 四、不做什么（刻意排除）

- 不加 Vault / Doppler / 1Password secrets integration：当前是单人项目，Vercel env vars + 本地 `.env.local` 已足够；加三方 SaaS 反而增加攻击面和运维成本。
- 不引入完整 CI secret scan pipeline：Gitleaks pre-commit 覆盖 90% 场景，主人是唯一 pusher，CI 层价值低。
- 不重写 `QuestionCard` 为 `useActionState` / Server Actions：虽然是 Next.js 16 新官方方向（[Next.js Docs · Error Handling](https://nextjs.org/docs/app/getting-started/error-handling)），但会牵动整个 `/api/attempts` 的 contract，属重构不属修 bug，放 P3 再谈。

---

## 五、执行顺序建议

```
今天 (2026-04-13)：
  1. 10 min  P1 — QuestionCard handleSubmit 加 try/catch/finally（剧本二）
  2. 30 min  P0-A — Gitleaks pre-commit + 全 history 扫描 baseline
  3. 45 min  P0-B — Supabase service_role + DashScope 轮换 + DashScope 配额上限

本周内：
  - P2 — SRS 双写（QuestionCard:71 和复习页二次评分重复）
  - P2 — CourseTabs 暴露 practice/progress/notes/library
```

---

## 六、引用（均 ≥2025 末/2026）

- [Supabase Docs · Understanding API keys](https://supabase.com/docs/guides/api/api-keys) — 新 `sb_publishable_` / `sb_secret_` 体系、legacy 迁移；持续更新中，2026 版。
- [Supabase Docs · Rotating Anon, Service, and JWT Secrets](https://supabase.com/docs/guides/troubleshooting/rotating-anon-service-and-jwt-secrets-1Jq6yd) — 服务端 key 零 downtime 轮换流程。
- [Supabase Discussion #39498 · Safely rotate service role key without breaking jobs](https://github.com/orgs/supabase/discussions/39498) — 2026 真实案例与"last used"指示器使用方式。
- [Alibaba Cloud Model Studio · How to get an API Key](https://www.alibabacloud.com/help/en/model-studio/get-api-key) — DashScope key 创建、RAM 禁用即 key 失效的官方说明。
- [AppSecSanta · Gitleaks vs TruffleHog (2026)](https://appsecsanta.com/sast-tools/gitleaks-vs-trufflehog) — 2026 基准对比：Gitleaks 适合 pre-commit、TruffleHog 适合 CI 验证活性。
- [OneUptime · Secret Scanning with gitleaks (2026-01-25)](https://oneuptime.com/blog/post/2026-01-25-secret-scanning-gitleaks/view) — 2026 年 1 月的实操指南，带 `.pre-commit-config.yaml` 样板。
- [BFG Repo-Cleaner 官方](https://rtyley.github.io/bfg-repo-cleaner/) — 10-720x 快于 filter-branch，当前仍是清 history 的首选。
- [Next.js Docs · Error Handling (App Router)](https://nextjs.org/docs/app/getting-started/error-handling) — `useActionState` + error.tsx 的 Next.js 16 官方错误处理心智模型（未来 P3 重构参考）。

---

**文档结束**。以上所有命令在主会话或主人 terminal 可直接 copy-paste 跑；所有 Edit 操作需在主会话用 Edit 工具，本调研 Agent 未修改 course-hub 任何文件。
