# COMP110 agenda.json Schema & Sample Data

**时间**: 2026-04-18 22:23
**目的**: 为 Phase 2 骨架实现定义 agenda.json 数据契约（Phase 3 迁移的前置条件）

---

## 背景

Phase 1 设计稿（mockup.html）展示了六种 badge 类型和三个时间分组（On the Horizon / This Week / The Past）。Phase 2 实现清单中 Phase 3 起点是"迁移 mockup.html 内容 → agenda.json schema"，本文定义该 schema。

---

## TypeScript 接口

```typescript
interface Resource {
  label: string;   // "Slides", "Notebook", "Panopto", "Gradescope"
  url: string;
}

interface AgendaItem {
  id: string;                              // "CL33", "EX08", "QZ03", "FN00"
  type: "CL" | "LS" | "EX" | "QZ" | "CQ" | "FN";
  title: string;
  date: string;                            // ISO 8601: "2026-04-18"
  resources?: Resource[];
  status: "upcoming" | "live" | "submitted" | "attended" | "read" | "due";
  dueDays?: number;                        // 仅 status="due" 时有效
  isToday?: boolean;
  isCancelled?: boolean;
}

interface Agenda {
  semester: string;        // "Spring 2026"
  instructor: string;      // "Kris Jordan"
  startDate: string;       // "2026-01-14"
  endDate: string;         // "2026-04-30"
  currentWeek: number;     // 13
  totalWeeks: number;      // 15
  items: AgendaItem[];
}
```

---

## 示例 agenda.json（4 条，符合 Apr 18 实际场景）

```json
{
  "semester": "Spring 2026",
  "instructor": "Kris Jordan",
  "startDate": "2026-01-14",
  "endDate": "2026-04-30",
  "currentWeek": 13,
  "totalWeeks": 15,
  "items": [
    {
      "id": "CL33",
      "type": "CL",
      "title": "CSV Data Analysis · Zip, Enumerate, Dict Comprehensions",
      "date": "2026-04-18",
      "resources": [
        {"label": "Slides", "url": "/resources/cl33-slides.pdf"},
        {"label": "Notebook", "url": "/resources/cl33-notebook.ipynb"},
        {"label": "Panopto", "url": "https://panopto.unc.edu/..."}
      ],
      "status": "live",
      "isToday": true
    },
    {
      "id": "QZ03",
      "type": "QZ",
      "title": "Quiz 3 · Lists, Dicts, and Iteration",
      "date": "2026-04-17",
      "resources": [
        {"label": "Concepts", "url": "/resources/qz3-concepts.md"},
        {"label": "Practice", "url": "/resources/qz3-practice.ipynb"},
        {"label": "Memory Diagram Rules", "url": "/resources/memory-rules.pdf"}
      ],
      "status": "submitted"
    },
    {
      "id": "EX08",
      "type": "EX",
      "title": "Linked List Utilities · Recursion over LinkedNode",
      "date": "2026-04-15",
      "resources": [
        {"label": "Instructions", "url": "/resources/ex08-spec.md"},
        {"label": "Starter Code", "url": "/resources/ex08-starter.py"},
        {"label": "Gradescope", "url": "https://gradescope.com/..."}
      ],
      "status": "submitted"
    },
    {
      "id": "FN00",
      "type": "FN",
      "title": "Final Examination",
      "date": "2026-04-30",
      "resources": [
        {"label": "Review Guide", "url": "/resources/final-review.md"},
        {"label": "Practice Problems", "url": "/resources/final-practice.pdf"},
        {"label": "Location: Hamilton 100", "url": "#"}
      ],
      "status": "due",
      "dueDays": 12
    }
  ]
}
```

---

## 说明

- `status` 由前端在运行时根据 `date` 和当前日期计算，`agenda.json` 里可以静态写入或省略让前端推断
- `currentWeek` / `totalWeeks` 用于顶部进度条
- `isToday` 可由前端计算，`agenda.json` 里不必维护
- Badge 颜色映射见 `comp110-phase2-impl-2026-04-18.md` 第 6 节
