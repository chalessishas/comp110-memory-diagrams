# Research Loop 00:04 — TOEFL Prose Summary 实施路径

**时间**：2026-04-17 00:04
**触发**：每小时 Research Loop（跨日首次 TOEFL-focused 报告）

---

## 1. 当前项目状态

### TOEFL

| 维度 | 状态 |
|------|------|
| Grammar | L60A/B + L61A/B/C + L62A/B/C + L63 + L64A/B + L66 + L67A + L68 = 16+ patterns ✅ |
| Reading passages | 3 篇 (Urban Agriculture, Deep Ocean, Plate Tectonics) × 12 题 = 36 总 ✅ |
| Question types implemented | vocab / detail / inference / attitude / purpose / negative_fact / sentence_simplification / text_insertion / reference / multiple = 10 types ✅ |
| **prose_summary** | ❌ 未实施 |
| calibration | 10/10 ✅ |

### 已知潜在 Bug

**`multiple` 类型在 `AcademicPassage.jsx` 中是单选行为**：
- `data.js` Q11: `correct: [0, 1, 2]`（正确格式）
- `handleSelect(idx)` 存 `answers[qi] = idx`（单数字，不是数组）
- `isCorrect(qIdx)` 判断 `answers[qIdx] === qs[qIdx].correct`（数字 === 数组 → 恒为 false）
- Urban Agriculture Q11 (`multiple`) 在 `DailyLifeReading.jsx` 中，需确认是否有独立 handler

这个 bug 必须在 `prose_summary` 实施时一并修复，否则 `prose_summary` 也会走错误路径。

---

## 2. Prose Summary 格式分析

### TOEFL 官方格式

- 出现位置：阅读文章**最后一题**（Q12-14 区间，通常是 Q12 或 Q13）
- 结构：给出 1 句 introductory sentence，要求从 6 选项中**选 3 个**完成 summary
- 分值：最多 **2 分**（选中 3 个 → 2 分；选中 2 个 → 1 分；选中 ≤1 个 → 0 分）
- 干扰项类型：细节正确但非主旨、段落误归、与原文矛盾

### 与现有 `multiple` 类型区别

| 特征 | `multiple` | `prose_summary` |
|------|-----------|----------------|
| 选择数 | 指定 N（如"select 3"） | 固定 3 of 6 |
| 分值 | 0 or 1（全中才得分） | 0/1/2 partial |
| Lead sentence | 无 | 有（段落概括句） |
| 位置 | 任意 | 固定最后一题 |
| 选项长度 | 短词汇/短句 | 1-2 句完整陈述 |

---

## 3. 实施设计

### 3a. 数据格式（pack6.js 新增字段）

```js
{
  id: 13,
  question_type: 'prose_summary',
  text: 'An introductory sentence for a brief summary of the passage is provided below. Complete the summary by selecting the THREE answer choices that express the most important ideas in the passage.',
  lead_sentence: 'Deep ocean environments present unique challenges that have driven the evolution of remarkable biological adaptations.',
  options: [
    'Hydrothermal vents create conditions that support chemosynthetic-based food webs.',
    'Deep sea creatures have developed adaptations like bioluminescence and pressure resistance.',
    // ... 4 more (3 correct + 3 distractors)
  ],
  correct: [0, 1, 3],  // indices of the 3 correct answers
  explanation: '...',
}
```

### 3b. UI 变更（AcademicPassage.jsx）

**新增函数：**

```js
// Multi-select handler for prose_summary and multiple types
const handleMultiSelect = (idx) => {
  const q = currentQ;
  const isMulti = q.question_type === 'prose_summary' || q.question_type === 'multiple';
  if (!isMulti) { handleSelect(idx); return; }

  const maxSelect = q.question_type === 'prose_summary' ? 3
    : Array.isArray(q.correct) ? q.correct.length : 1;
  const current = answers[currentQuestion] || [];
  if (current.includes(idx)) {
    setAnswers({ ...answers, [currentQuestion]: current.filter(i => i !== idx) });
  } else if (current.length < maxSelect) {
    setAnswers({ ...answers, [currentQuestion]: [...current, idx] });
  }
};
```

**UI checkbox 而非 radio：**
- `isSelected = Array.isArray(answers[qi]) ? answers[qi].includes(idx) : answers[qi] === idx`
- 方形 checkbox 图标取代圆圈

**Lead sentence 展示：**
```jsx
{currentQ.lead_sentence && (
  <div style={{ /* subtle box */ }}>
    {currentQ.lead_sentence}
  </div>
)}
```

### 3c. 评分逻辑变更

```js
// isCorrect 需支持 partial credit
const scoreQuestion = (qIdx) => {
  const q = qs[qIdx];
  const ans = answers[qIdx];
  if (q.question_type === 'prose_summary') {
    if (!Array.isArray(ans)) return { correct: false, points: 0, maxPoints: 2 };
    const matches = ans.filter(a => q.correct.includes(a)).length;
    return { correct: matches === 3, points: Math.max(0, matches - 1), maxPoints: 2 };
  }
  if (Array.isArray(q.correct)) {
    const matched = Array.isArray(ans) && ans.length === q.correct.length
      && ans.every(a => q.correct.includes(a));
    return { correct: matched, points: matched ? 1 : 0, maxPoints: 1 };
  }
  return { correct: ans === q.correct, points: ans === q.correct ? 1 : 0, maxPoints: 1 };
};
```

---

## 4. 实施工作量评估

| 任务 | 文件 | 预估行数 | 难度 |
|------|------|---------|------|
| 修复 `multiple` 类型 bug | `AcademicPassage.jsx` | +20 | Low |
| 添加 `prose_summary` UI | `AcademicPassage.jsx` | +40 | Medium |
| 评分逻辑更新 | `AcademicPassage.jsx` | +15 | Low |
| 添加 typeLabels/Colors | `data.js` | +4 | Low |
| 数据：3 篇各加 Q13 prose_summary | `pack6.js` | +120 | Medium (质量) |
| **总计** | | **~200 行** | **Medium** |

**总工时预估：60-90 分钟**（写数据最耗时，prose summary 选项需有说服力的干扰项）。

---

## 5. 优先级决策

HOLD 理由（进行评估）：
- 现在是凌晨，用户不在场
- 中等工作量（不是 5 分钟的 regex 添加）
- 数据质量要求高（需要 2 好 1 坏或更多组合的干扰项）

**建议**：在用户醒来后主动提议实施。若 Progress Loop 触发时用户在场或已有明确指令，可立即开始。

---

## 6. 其他待观察事项

### course-hub

上次 chronicle 显示（2026-04-16 18:45 op-0416j）：
- **13 HIGH CVEs 跨 5 个项目**（npm audit）
- **prod 漂移 177 commits**（等待用户授权 push）

两件事都需要主人决策，不可自动执行。

### ai-text-detector

参见同日 `2026-04-17-research-loop-0000-ai-detector-restart.md`。
dataset_v6.jsonl 已就绪，等待用户手动触发 Colab A100 训练。

---

## Sources

- TOEFL Reading question type specs: https://www.ets.org/toefl/test-takers/ibt/about/content/reading.html
- Prose Summary partial credit scoring: TOEFL iBT® Official Guide (ETS, 2023 ed.), Reading section explanation
- Internal: `TOEFL/src/reading/AcademicPassage.jsx` (lines 47-59, 311-332)
- Internal: `TOEFL/src/data.js` (lines 107-114, 142-143) — `multiple` type using array correct
