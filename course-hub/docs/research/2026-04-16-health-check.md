# course-hub 健康度巡检报告（2026-04-16 18:25）

自动由 Progress Loop 触发执行，主人不在场。本文件供主人回来后决策参考。

## 一、本地代码健康度 ✅

| 检查 | 结果 |
|------|------|
| `npx tsc --noEmit` | PASS |
| `npm run build` | PASS（22 个路由全部 build 成功） |
| 工作区状态 | clean（无 uncommitted changes） |

结论：本地代码编译一切正常，Next.js 16 + React 19 + @ai-sdk 的版本组合没有出现生态不兼容。

## 二、Vercel 部署状态 🔴 严重漂移

- **最新 prod**：`dpl_9eNnbfozcH4MpvULABdVWLK96hMV`
- **Prod commit**：`13ed14e1` "feat: learn page shows exam scope badges on in-scope knowledge points"
- **Prod 时间**：2026-04-07 22:41（Tue）
- **Main HEAD**：`4c9cb3f` (2026-04-11 23:38)
- **漂移 commit 数**：`git log 13ed14e..HEAD -- course-hub/` = **177 个**

### 未上线的关键内容

1. **安全修复（9 个 API 的 ownership/IDOR 修复）**
   - `5fddc4b` fix(security): ownership checks for exam-prep, exam-scope, chunks, mistake-patterns
   - `a7b1c65` fix(security): ownership checks for exams, share, uploads, teach-back, extract
   - `f7da06e` fix(course-hub): close 3 IDOR gaps + i18n day names
   - `fe744ff` fix(security): ownership checks for courses GET, questions, outline-nodes POST
   - `352b503` fix(course-hub): upload courseId ownership + parse storage path validation
   - `edb2f8d` refactor(course-hub): extract verifyCourseOwnership helper + fix 3 missing ownership checks

2. **Phase 4 Evidence-Based Optimization**（SSE streaming / FSRS exam-day retrievability / interleaving / concreteness fading）

3. **Phase 5 User-Requested Features**（exam scope filter 接入 review 页 / term explanation cards / dashboard due-count badges / session summary modal）

4. **Phase 6 Evidence-Based Mastery System**（mastery pipeline 完整写入 / adaptive difficulty / teach-back / metacognitive confidence / explanation gating / misconception lifecycle / FSRS server sync / per-question attempt history badge / RSC query parallelization）

5. **i18n sprint**（478 keys × 2 locales）

6. **auth 中间件 + 暗色模式开关**（f353eec）

### 漂移根因

STATUS.md Apr 6/7 记录："Vercel Git integration not auto-deploying (manual `npx vercel deploy --prod` works)"。主人手动部署后未再次执行，.github/workflows/deploy-course-hub.yml 已建但未激活（需要 3 个 GitHub Secrets: VERCEL_TOKEN / VERCEL_ORG_ID / VERCEL_PROJECT_ID）。

## 三、Supabase 状态 ⚠️ 5 个 WARN

项目：`zubvbcexqaiauyptsyby` (course-hub)
状态：ACTIVE_HEALTHY
Postgres 版本：17.6.1.104

### Security advisors（5 个 WARN，均为 EXTERNAL facing）

| # | 名称 | 对象 | 修复 |
|---|------|------|------|
| 1 | function_search_path_mutable | `public.set_updated_at` | `ALTER FUNCTION set_updated_at() SET search_path = public, pg_temp` |
| 2 | function_search_path_mutable | `public.set_updated_at_v2` | 同上 |
| 3 | function_search_path_mutable | `public.upsert_outline_nodes` | 同上 |
| 4 | function_search_path_mutable | `public.replace_outline` | 同上 |
| 5 | auth_leaked_password_protection | Auth 全局 | Dashboard → Auth → Password Settings → 启用 HIBP 检查 |

### Migration 混乱 🟡

对比本地 `course-hub/supabase/migrations/*.sql` 与远程 `list_migrations` 输出：

- 本地有两个 `010_*`（`010_fix_storage_policies.sql` + `010_learning_system_v2.sql`）——**文件名编号冲突**
- 本地 `013_key_terms.sql` 在远程对应 `add_key_terms_to_lesson_chunks`（名称不一致）
- 远程有本地没有的 `018b_fsrs_cards_learning_steps` 和 `fsrs_review_logs_unique`（孤儿 migration）
- 远程 `020_drop_duplicate_rls_policies` 被 apply 了**两次**（timestamps 20260410134947 + 20260410135153）
- 本地 `001-009_*.sql` 在远程 migrations 列表里不存在——**早期用 SQL Editor 直接跑的，未登记**

影响：下次 `supabase db push` 行为不可预测，可能触发重复 apply 或跳过。

## 四、已起草但未执行的修复

见同目录 `2026-04-16-021-function-search-path-draft.sql` —— 修 4 个 search_path 警告的 migration 草稿。故意放在 `docs/research/` 而不是 `supabase/migrations/`，避免被 `db push` 误 apply。主人授权后移动到 migrations 目录即可。

## 五、待主人决策的行动清单

按优先级：

1. **P0 — 授权 `npx vercel deploy --prod`**：上线 177 个 commit（含 IDOR 修复），5 分钟动作。建议先本地 `npm run build` 再 deploy（已验证通过）。
2. **P1 — 激活 Vercel CI/CD**：加 3 个 GitHub Secrets 让 `.github/workflows/deploy-course-hub.yml` 生效，避免下次漂移。
3. **P2 — Apply `021_fix_function_search_path.sql`**：修 4 个 search_path 警告，纯 ALTER FUNCTION，零数据风险。
4. **P3 — Dashboard 开 Leaked Password Protection**：手动操作，30 秒。
5. **P4 — 整理 migration 文件夹**：解决 010 编号冲突 + 命名不一致，需要主人确认 migration state 基线。

## 六、零风险已执行的动作

本次 Progress Loop 未执行任何 prod-touching 动作。仅：
- 读操作（git log / Supabase / Vercel MCP）
- 写 `docs/research/2026-04-16-health-check.md`（本文件）
- 写 `docs/research/2026-04-16-021-function-search-path-draft.sql`（草稿）
- 写 `docs/chronicle/2026-04-16.md` Turn 记录

Zero prod state mutation.
