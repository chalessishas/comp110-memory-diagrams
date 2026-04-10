# CourseHub: Supabase RLS Performance Optimization

> 调研日期: 2026-04-10 04:23  
> 触发: Research Loop（第七次）  
> 来源: Supabase 官方文档 + Discussion #14576

---

## 核心发现：`auth.uid()` vs `(select auth.uid())`

### 问题

Postgres 在评估 RLS 策略时，对 `auth.uid()` 的调用方式影响性能：

```sql
-- ❌ 慢：Postgres 对每一行都调用一次 auth.uid()
FOR ALL USING (user_id = auth.uid())

-- ✅ 快：Postgres 将结果缓存为 initPlan，整个语句只调用一次
FOR ALL USING (user_id = (select auth.uid()))
```

**性能差异**：Supabase 官方测试显示，对大表（10k+ 行）的查询，`(select auth.uid())` 可将查询时间从 450ms 降至 45ms（**10x**）。

### 受影响的表（已识别）

| 表 | 受影响行数预期 | 当前策略 |
|----|--------------|---------|
| `element_mastery` | 高（每 KP × 每用户多条记录）| ❌ 裸 auth.uid() |
| `misconceptions` | 中 | ❌ 裸 auth.uid() |
| `challenge_logs` | 高（每次练习一条）| ❌ 裸 auth.uid() |
| `lesson_progress` | 中 | ❌ 裸 auth.uid() |
| `attempts` | 高（每次答题一条）| ❌ 裸 auth.uid() |
| `courses` | 低（每用户几门课）| ❌ 裸 auth.uid()（影响小）|
| `question_bookmarks` | 中 | ❌ 裸 auth.uid() |
| `prerequisite_skips` | 低 | ❌ 裸 auth.uid() |

**已处理**：创建 `supabase/migrations/014_rls_performance.sql` 修复上述全部表。

### 不需要修改的表

`outline_nodes`、`uploads`、`questions`、`study_tasks`、`lessons` 等使用 `exists (select 1 from courses where ... auth.uid())` 形式——这是 JOIN 子查询，`auth.uid()` 本身已经在 EXISTS 子查询内部，不是逐行调用的热点。

---

## 其他 RLS 优化发现

### 1. `FOR ALL` 拆分为独立策略

Supabase 文档建议将 `FOR ALL` 拆分为 `FOR SELECT`/`FOR INSERT`/`FOR UPDATE`/`FOR DELETE`，以便 Postgres 优化器针对每种操作单独使用索引。

**当前评估**：本项目大多数表上的操作均是全 CRUD，且数据量在 MVP 阶段不会到需要此优化的量级。**暂不实施**，上线后通过 `EXPLAIN ANALYZE` 确认是否必要。

### 2. N+1 查询

当前代码中，`mistake-patterns/route.ts` 的聚合查询先取 questions，再取 attempts，逻辑上是两次查询，但已用 IN 批量拉取——符合最佳实践，不存在 N+1。

---

## 实施状态

| 操作 | 状态 |
|------|------|
| `014_rls_performance.sql` 迁移文件创建 | ✅ 完成 |
| 应用到 Supabase 生产数据库 | ⏳ 需用户执行 `supabase db push` 或在 Supabase SQL Editor 运行 |

**执行方式**（两选一）：
```bash
# 方式 1: Supabase CLI
supabase db push

# 方式 2: 复制 014_rls_performance.sql 内容到 Supabase Dashboard → SQL Editor → Run
```

---

## 参考

- [Supabase RLS Performance Best Practices](https://supabase.com/docs/guides/troubleshooting/rls-performance-and-best-practices-Z5Jjwv)
- [Discussion #14576: RLS Performance](https://github.com/orgs/supabase/discussions/14576)
