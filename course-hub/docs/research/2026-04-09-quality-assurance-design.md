# CourseHub 质量保证与持续改进体系设计

> **日期**: 2026-04-09
> **触发**: 用户提出三个核心问题：(1) AI 出题正确性保证 (2) 外部知识源接入 (3) 自审查/持续改进机制
> **发现**: 数据采集层已完整，但反馈数据从未被消费——系统是开环的

---

## 一、现状审计：已有什么 vs 缺什么

### ✅ 已有的数据采集层

| 组件 | 位置 | 采集内容 |
|------|------|----------|
| `question_feedback` 表 | `005_question_feedback.sql` | 用户对题目的反馈 (wrong_answer/unclear/too_easy/too_hard/duplicate/irrelevant) |
| 反馈 UI | `QuestionCard.tsx` L202-229 | 答题后出现 4 个药丸按钮，单击即反馈 |
| 反馈 API | `POST /api/questions/[id]/feedback` | upsert，每用户每题仅一次 |
| `attempts` 表 | `001_initial_schema.sql` | 每次答题记录 (user_answer, is_correct, answered_at) |
| `misconceptions` 表 | `010_learning_system_v2.sql` | AI 检测的错误概念 (occurrence_count, relapse_count, resolved 状态) |
| `challenge_logs` 表 | `010_learning_system_v2.sql` | AI 会话日志 (misconceptions_found[], elements_passed/failed) |
| 错误率聚合 API | `GET /api/courses/[id]/mistake-patterns` | 按 KP 聚合错误率 (wrong/total, unique_questions) |
| 错误热点 UI | `MistakePatterns.tsx` | review 页顶部展示 Top 5 薄弱 KP |
| FSRS 记忆追踪 | `spaced-repetition.ts` | 每张卡片的 stability/difficulty/reps/lapses |

### ❌ 缺失的反馈处理层

| 缺口 | 影响 | 严重度 |
|------|------|--------|
| **反馈数据从未被读取** | `question_feedback` 写入后无任何代码读取/消费 | 🔴 Critical |
| **无自动标记/下架** | 被多人报告 "wrong_answer" 的题目仍正常出现 | 🔴 Critical |
| **无错误概念注入** | `misconceptions` 数据不参与 `generateQuestionsFromOutline` 的 prompt | 🟡 High |
| **无统计异常检测** | 95% 用户做错某 MCQ → 可能答案错，但无告警 | 🟡 High |
| **无 AI 自验证** | AI 生成题目后直接入库，无第二次验证 | 🟡 High |
| **无教学效果反馈** | FSRS 数据不用于评估 lesson 质量 | 🟠 Medium |
| **无管理视图** | 无法看到跨用户的题目质量聚合 | 🟠 Medium |

**结论**：系统不是"没有质量保证"——数据采集完整，但处于**开环状态**。数据流向 DB 后即止，从未回流到生成管线。

---

## 二、闭环设计：三条反馈回路

### 回路 1：题目质量闭环 (Question Quality Loop)

```
用户答题 → attempts 记录
         → 用户点反馈药丸 → question_feedback
              ↓
         [NEW] 异常检测 Trigger
              ↓
         1. 统计指标超阈值 → 标记 question.flagged = true
         2. 被标记题目不再出现在练习/复习队列
         3. [可选] AI 二次验证被标记题目 → 修正或确认删除
```

**触发条件（任一即标记）**：
- `wrong_answer` 反馈 ≥ 2 个独立用户
- 单题答对率 < 15%（且 attempt 数 ≥ 5）
- MCQ 选项分布均匀（无明显正确答案，χ² 检验 p > 0.5）

**实现方案**：

```sql
-- Migration: 添加 flagged 列
ALTER TABLE public.questions ADD COLUMN flagged boolean DEFAULT false;
ALTER TABLE public.questions ADD COLUMN flagged_reason text;
ALTER TABLE public.questions ADD COLUMN flagged_at timestamptz;
```

```typescript
// API: POST /api/admin/question-quality-check
// 1. 查询被 ≥2 人报告 wrong_answer 的题目
// 2. 查询 attempt 正确率 < 15% 的题目
// 3. 批量标记 flagged = true + reason
// 4. 前端过滤: questions.filter(q => !q.flagged)
```

**投入**: ~3h（migration + API + 前端过滤）

### 回路 2：错误概念 → 出题注入 (Misconception Injection Loop)

```
用户做错题 → misconception 被记录
         ↓
    [NEW] generateQuestionsFromOutline 读取该 KP 的 misconceptions
         ↓
    prompt 注入: "学生常见错误概念: [xxx], 请设计针对性干扰项"
         ↓
    生成的 MCQ 干扰项基于真实错误，而非 AI 臆想
```

**实现方案**：

```typescript
// 修改 generate-questions/route.ts
// 在调用 generateQuestionsFromOutline 前，查询每个 KP 的 misconceptions
const { data: misconceptions } = await supabase
  .from("misconceptions")
  .select("misconception_description, occurrence_count, concept_id")
  .in("concept_id", batch.map(kp => kp.id))
  .eq("resolved", false)
  .order("occurrence_count", { ascending: false })
  .limit(10);

// 将 misconceptions 传入 AI prompt
const miscByKp = groupBy(misconceptions, "concept_id");
// prompt 追加:
// "Known student misconceptions for each KP:
//  - [KP Title]: [misconception_description] (occurred N times)"
```

**价值**: AI 目前靠猜测学生可能的错误来设计干扰项。接入真实 misconceptions 后，干扰项精确度大幅提升 → 做对≠理解，做错=精确定位误解。

**投入**: ~3h（route 修改 + prompt 增强）

### 回路 3：教学效果评估 (Teaching Effectiveness Loop)

```
学生学完 lesson → 做练习 → FSRS 追踪记忆
         ↓
    [NEW] 24h 后测量 first-attempt accuracy (延迟测试)
         ↓
    KP 级别的"教学有效性分数" = 延迟首次正确率
         ↓
    低效 lesson → 触发重新生成（不同 prompt/更多 examples）
```

**测量方法**：
- **延迟准确率**: 学完 lesson 后 ≥24h 的首次答题正确率
- **FSRS stability**: 高 stability = 记住了 = 教得好
- **每 KP 样本量**: ≥3 次延迟答题才计算

**投入**: ~6h（统计 API + lesson 效果仪表盘 + 条件重生成）

---

## 三、AI 自验证设计 (Generation-time Self-check)

### 当前生成流程的问题

```
AI 生成 JSON → Zod 验证格式 → 直接入库
               ↑ 只验证格式    ↑ 不验证正确性
```

MCQ 答案可能标错、fill_blank 答案可能有多种合理表述、short_answer 关键词可能不全。

### 方案：验证管线 (Generation + Verification Pipeline)

```
AI Call 1: generateQuestionsFromOutline (现有)
    ↓
AI Call 2: verifyQuestions (新增)
    - 输入: 生成的题目 + KP 上下文
    - 验证:
      a. MCQ: AI 独立解题，答案是否一致？
      b. fill_blank: 是否有多个合理答案？列出替代答案
      c. short_answer: 评分标准是否合理？
      d. 题干是否有歧义？
    - 输出: { verified: boolean, corrections: [...], confidence: number }
    ↓
verified=true → 入库
verified=false → 应用 corrections 后重新验证，或丢弃
```

**Token 成本分析**：
- 当前: 每次生成 ~1000 tokens (5 KPs × 3 questions)
- 新增验证: ~500 tokens
- 增幅: +50% token cost (~$0.39/M → ~$0.58/M)
- 以 100 题/用户/月计算: 增加约 $0.02/用户/月
- **结论**: 成本可忽略

**投入**: ~4h

### 替代答案扩展 (fill_blank/short_answer)

当前的 `attempts/route.ts` 判分逻辑很脆弱：

```typescript
// fill_blank: 仅 exact | contains | numeric ±0.001
// short_answer: 单词重叠 ≥50%（3字母以上）
```

**问题**: "derivative" 和 "the derivative of f" 都可能是正确答案，但当前逻辑可能判错。

**方案**: 在验证阶段让 AI 列出所有合理的替代答案，存入 `questions.alternative_answers jsonb`，判分时检查替代答案。

```sql
ALTER TABLE public.questions ADD COLUMN alternative_answers jsonb DEFAULT '[]';
```

---

## 四、外部知识源接入评估

### 用户问题：能否从 YouTube/网络/教科书获取题目？

| 来源 | 可行性 | 版权风险 | 数据质量 | 推荐度 |
|------|--------|----------|----------|--------|
| **OpenStax** (openstax.org) | ✅ API + 下载 | CC BY 4.0 ✅ | 经专家审核 ✅ | ⭐⭐⭐⭐⭐ |
| **MIT OCW** (ocw.mit.edu) | ✅ 公开下载 | CC BY-NC-SA ✅ | 高质量 ✅ | ⭐⭐⭐⭐ |
| **Khan Academy** | ⚠️ 无公开 API | CC BY-NC-SA ⚠️ | 高质量 ✅ | ⭐⭐⭐ |
| **YouTube 教学视频** | ⚠️ 字幕提取 | ❌ 版权复杂 | 参差不齐 ❌ | ⭐⭐ |
| **Wikipedia** | ✅ API | CC BY-SA ✅ | 中等（非教学） | ⭐⭐ |
| **网络爬虫** | ⚠️ 技术可行 | ❌ 版权地雷 | 不可控 ❌ | ⭐ |

### 推荐方案：OpenStax 作为 RAG 知识源

**为什么 OpenStax 是最佳选择**：
1. CC BY 4.0 — 可商用、可改编、只需署名
2. 覆盖主流大学课程（微积分、物理、化学、生物、经济学、心理学等）
3. 内容经教授团队审核，准确性有保证
4. 提供结构化数据（章节 → 节 → 练习题，已分好类）

**接入方式**：
```
1. 下载 OpenStax 教材 CNXML/HTML 源文件（~20 本常用教材）
2. 解析为 KP → 练习题 映射
3. 用于两个场景:
   a. Ground Truth: AI 生成的答案 vs OpenStax 标准答案 → 交叉验证
   b. 题库补充: 当 AI 生成题目被标记 flagged 时，fallback 到 OpenStax 原题
```

**投入**: ~12h（教材解析 + embedding 索引 + RAG 接入管线）

---

## 五、"吾日三省吾身"——系统自我进化机制

### 问题重述

> 对于 AI 来说，如何保证这个项目一直在更进而不是停滞？

这是一个**系统论**问题。CourseHub 的 AI 目前是**无状态函数**——每次调用独立，不记住历史表现，不从错误中学习。

### 设计：三省机制

#### 省一：日常指标监控 (Daily Health Check)

```sql
-- 每日自动运行的健康检查查询
WITH daily_stats AS (
  SELECT
    date_trunc('day', a.answered_at) AS day,
    COUNT(*) AS total_attempts,
    AVG(CASE WHEN a.is_correct THEN 1 ELSE 0 END) AS accuracy,
    COUNT(DISTINCT a.question_id) AS unique_questions,
    COUNT(DISTINCT f.question_id) FILTER (WHERE f.reason = 'wrong_answer') AS reported_wrong
  FROM attempts a
  LEFT JOIN question_feedback f ON f.question_id = a.question_id
  GROUP BY 1
)
SELECT * FROM daily_stats ORDER BY day DESC LIMIT 7;
```

**告警阈值**：
- 整体正确率 < 30% 或 > 90% → 题目难度分布异常
- `reported_wrong` / `unique_questions` > 5% → 质量问题
- 某科目正确率突变 > 20pp → 可能生成了一批错题

#### 省二：周度 Prompt 复盘 (Weekly Prompt Review)

```
每周一触发:
1. 查询上周被标记 flagged 的题目
2. 分析标记原因分布 (wrong_answer vs unclear vs too_hard)
3. 如果 wrong_answer 占比 > 40%:
   → AI 的答案生成有系统性问题
   → 触发 prompt 修改: 加强 "verify your answer by solving the problem step by step"
4. 如果 unclear 占比 > 30%:
   → 题干表述有问题
   → 触发 prompt 修改: 加强 "ensure the question stem is unambiguous"
5. 将修改后的 prompt 版本号 +1，记录在 docs/prompts/changelog.md
```

#### 省三：月度效能评估 (Monthly Effectiveness Report)

```
每月1号触发:
1. 计算每个 KP 的"教学有效性分数" (延迟首次正确率)
2. 排名 Bottom 10% 的 KP → 教学内容需要改进
3. 分析这些 KP 的 lesson 内容:
   - 是否缺少 concrete examples?
   - 是否 concreteness fading 层级不合适?
   - 是否 checkpoint 类型需要调整?
4. 为 Bottom 10% KP 重新生成 lesson（带改进后的 prompt）
5. 对比前后的延迟正确率 → A/B 测试效果
```

---

## 六、实施优先级

| 阶段 | 任务 | 投入 | 影响 | 前置条件 |
|------|------|------|------|----------|
| **P0** | 题目标记 + 前端过滤 (flagged 列 + 异常检测) | 3h | 🔴 防止错题伤害用户 | 无 |
| **P1** | AI 自验证管线 (generation + verification) | 4h | 🔴 从源头减少错题 | 无 |
| **P1** | 错误概念注入出题 prompt | 3h | 🟡 提升干扰项精确度 | 无 |
| **P2** | 替代答案扩展 (alternative_answers) | 2h | 🟡 减少误判"答对→判错" | P1 |
| **P2** | 日常健康检查 SQL + 告警 | 2h | 🟡 系统性监控 | P0 |
| **P3** | OpenStax RAG 接入 | 12h | 🟡 交叉验证 + 题库补充 | P0+P1 |
| **P3** | 教学效果评估仪表盘 | 6h | 🟠 长期优化循环 | 需积累数据 |
| **P4** | Prompt A/B 测试框架 | 8h | 🟠 科学化迭代 | P3 |

**总投入**: ~40h (约 1 周全职)
**建议**: P0+P1 先做（10h），闭合最关键的质量环路，其余按需迭代。

---

## 七、架构变更总览

```
                    ┌─────────────────────┐
                    │   AI Generation     │
                    │  (Qwen 3.5-Plus)    │
                    └─────┬───────────────┘
                          │
                    ┌─────▼───────────────┐
           NEW ───→ │   AI Verification   │ ←─── NEW
                    │  (second AI call)   │
                    └─────┬───────────────┘
                          │
                    ┌─────▼───────────────┐
                    │    Zod Validation   │ (已有)
                    └─────┬───────────────┘
                          │
                    ┌─────▼───────────────┐
                    │     DB Storage      │ (已有)
                    └─────┬───────────────┘
                          │
              ┌───────────┼───────────────┐
              │           │               │
     ┌────────▼─┐  ┌──────▼────┐  ┌───────▼──────┐
     │ attempts │  │ feedback  │  │misconceptions│  (已有)
     └────┬─────┘  └─────┬─────┘  └──────┬───────┘
          │              │               │
          └──────────────┼───────────────┘
                         │
                   ┌─────▼──────────────┐
          NEW ───→ │  Anomaly Detection │ ←─── NEW
                   │  (daily + weekly)  │
                   └─────┬──────────────┘
                         │
              ┌──────────┼──────────────┐
              │          │              │
     ┌────────▼──┐ ┌─────▼────┐ ┌──────▼─────┐
     │  Flag Q   │ │ Inject   │ │ Prompt     │  NEW
     │  in DB    │ │ to Prompt│ │ Versioning │
     └───────────┘ └──────────┘ └────────────┘
```

从**单向数据流** (生成 → 存储 → 展示) 变为**闭环** (生成 → 存储 → 展示 → 反馈 → 检测 → 改进生成)。
