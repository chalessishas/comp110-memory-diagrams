-- Migration 021: fix function_search_path_mutable warnings
-- Draft by Progress Loop 2026-04-16 18:25 — NOT YET APPLIED
-- 修复 Supabase security advisor 的 4 个 function_search_path_mutable WARN
--
-- 为什么：未设置 search_path 的 SECURITY DEFINER 函数存在被 schema 污染攻击
-- 的理论风险 —— 攻击者可创建同名对象诱导函数解析到恶意实现。
--
-- 安全性：这 4 个函数均为内部使用，设置 search_path 不改变行为。
--
-- 运行方式：主人授权后将本文件移到 course-hub/supabase/migrations/ 并命名
-- 021_fix_function_search_path.sql，然后 `supabase db push` 或用 MCP apply。

-- set_updated_at (trigger 函数，6 个表在用)
ALTER FUNCTION public.set_updated_at() SET search_path = public, pg_temp;

-- set_updated_at_v2 (014_rls_performance 引入)
ALTER FUNCTION public.set_updated_at_v2() SET search_path = public, pg_temp;

-- replace_outline (007_outline_upsert_rpc — 早期 SQL Editor 跑的)
ALTER FUNCTION public.replace_outline(uuid, jsonb) SET search_path = public, pg_temp;

-- upsert_outline_nodes (011_outline_upsert_atomic)
ALTER FUNCTION public.upsert_outline_nodes(uuid, jsonb) SET search_path = public, pg_temp;

-- 验证：apply 后 `SELECT get_advisors project_id=zubvbcexqaiauyptsyby type=security`
-- 应该看到这 4 个 function_search_path_mutable WARN 消失，只剩 auth_leaked_password_protection
-- （后者需要在 Dashboard 手动开启，不能用 SQL 修）。
