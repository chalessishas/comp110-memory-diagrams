# CourseHub API Reference

> 本文档覆盖 CourseHub 全部 API 端点。所有端点均为 Next.js App Router API Routes。

---

## 快速参考表

| 方法 | 路径 | 描述 | 认证 | AI |
|------|------|------|------|-----|
| GET | `/api/courses` | 获取用户所有课程 | 需要 | 否 |
| POST | `/api/courses` | 创建课程 | 需要 | 否 |
| GET | `/api/courses/[id]` | 获取单个课程详情 | 需要 | 否 |
| PATCH | `/api/courses/[id]` | 更新课程信息 | 需要 | 否 |
| DELETE | `/api/courses/[id]` | 删除课程 | 需要 | 否 |
| POST | `/api/courses/[id]/share` | 生成/获取分享链接 | 需要 | 否 |
| DELETE | `/api/courses/[id]/share` | 删除分享链接 | 需要 | 否 |
| POST | `/api/courses/fork` | 通过分享链接复制课程 | 需要 | 否 |
| GET | `/api/courses/[id]/outline` | 获取课程大纲节点 | 需要 | 否 |
| PUT | `/api/courses/[id]/outline` | 批量替换大纲节点 | 需要 | 否 |
| POST | `/api/outline-nodes` | 创建大纲节点 | 需要 | 否 |
| PATCH | `/api/outline-nodes/[id]` | 更新大纲节点 | 需要 | 否 |
| DELETE | `/api/outline-nodes/[id]` | 删除大纲节点 | 需要 | 否 |
| GET | `/api/courses/[id]/lessons` | 获取课程所有课时 | 需要 | 否 |
| POST | `/api/courses/[id]/lessons` | 批量生成课时（全部知识点） | 需要 | Qwen |
| POST | `/api/courses/[id]/lessons/generate-one` | 为单个知识点生成课时（支持 SSE） | 需要 | Qwen |
| GET | `/api/courses/[id]/lessons/[lessonId]/chunks` | 获取课时分块内容 | 需要 | 否 |
| POST | `/api/courses/[id]/lessons/[lessonId]/progress` | 更新学习进度 | 需要 | 否 |
| POST | `/api/courses/[id]/generate` | 生成学习任务 | 需要 | Qwen |
| POST | `/api/courses/[id]/generate-questions` | 生成练习题 | 需要 | Qwen |
| POST | `/api/courses/[id]/regenerate` | 翻译大纲并重新生成全部内容 | 需要 | Qwen |
| POST | `/api/courses/[id]/extract` | 从文件提取知识内容 | 需要 | Qwen |
| POST | `/api/courses/[id]/chat` | 课程 AI 助手对话（流式） | 需要 | Qwen |
| POST | `/api/courses/[id]/exam-prep` | 根据考试范围生成练习题 | 需要 | Qwen |
| GET | `/api/courses/[id]/exam-scope` | 获取课程知识点列表 | 需要 | 否 |
| POST | `/api/courses/[id]/exam-scope` | 解析考试范围文本匹配知识点 | 需要 | Qwen |
| GET | `/api/courses/[id]/export-anki` | 导出 Anki 格式闪卡 | 需要 | 否 |
| GET | `/api/courses/[id]/mastery` | 获取知识点掌握度 | 需要 | 否 |
| GET | `/api/courses/[id]/exams` | 获取考试日期列表 | 需要 | 否 |
| POST | `/api/courses/[id]/exams` | 创建考试日期 | 需要 | 否 |
| DELETE | `/api/courses/[id]/exams` | 删除考试日期 | 需要 | 否 |
| GET | `/api/courses/[id]/mistake-patterns` | 获取错题模式分析 | 需要 | 否 |
| POST | `/api/parse` | 解析教学大纲/考试文件 | 需要 | Qwen |
| POST | `/api/upload` | 上传文件到存储 | 需要 | 否 |
| GET | `/api/courses/[id]/uploads` | 获取课程上传文件列表 | 需要 | 否 |
| DELETE | `/api/courses/[id]/uploads` | 删除上传文件 | 需要 | 否 |
| POST | `/api/courses/[id]/notes` | 创建课程笔记 | 需要 | 否 |
| POST | `/api/courses/[id]/notes/organize` | AI 整理笔记内容 | 需要 | Qwen |
| GET | `/api/bookmarks` | 获取用户收藏题目 | 需要 | 否 |
| POST | `/api/bookmarks` | 收藏题目 | 需要 | 否 |
| DELETE | `/api/bookmarks` | 取消收藏 | 需要 | 否 |
| GET | `/api/questions?courseId=` | 获取课程题目（打乱顺序） | 需要 | 否 |
| POST | `/api/questions` | 从文件导入题目 | 需要 | Qwen |
| POST | `/api/questions/[id]/feedback` | 题目反馈 | 需要 | 否 |
| POST | `/api/attempts` | 提交答题记录 | 需要 | 否 |
| PATCH | `/api/study-tasks/[id]` | 更新学习任务状态 | 需要 | 否 |
| POST | `/api/preview/learning` | 预览 AI 生成内容 | 需要 | Qwen |

---

## 1. 课程管理

### GET /api/courses

**描述**: 获取当前用户的所有课程列表，按创建时间倒序

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**: 无

**响应**:

| 字段 | 类型 | 说明 |
|------|------|------|
| (数组) | `Course[]` | 课程对象数组 |
| id | string | 课程 UUID |
| title | string | 课程标题 |
| description | string \| null | 课程描述 |
| professor | string \| null | 教授名称 |
| semester | string \| null | 学期 |
| user_id | string | 所属用户 ID |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 401 | 未登录 |
| 500 | 数据库查询失败 |

---

### POST /api/courses

**描述**: 创建新课程

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 课程标题 |
| description | string | 否 | 课程描述 |
| professor | string | 否 | 教授名称 |
| semester | string | 否 | 学期 |

> 请求体经 `courseCreateSchema`（Zod）校验

**响应**: 返回创建的课程对象

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 参数校验失败 |
| 401 | 未登录 |
| 500 | 数据库插入失败 |

---

### GET /api/courses/[id]

**描述**: 获取单个课程详情

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |

**响应**: 完整课程对象

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 401 | 未登录 |
| 404 | 课程不存在 |

---

### PATCH /api/courses/[id]

**描述**: 更新课程信息

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |
| title | string | 否 | 新标题 |
| description | string | 否 | 新描述 |
| professor | string | 否 | 新教授 |
| semester | string | 否 | 新学期 |

> 请求体经 `courseUpdateSchema`（Zod）校验

**响应**: 返回更新后的课程对象

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 参数校验失败 |
| 401 | 未登录 |
| 500 | 更新失败 |

---

### DELETE /api/courses/[id]

**描述**: 删除课程（级联删除相关数据）

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |

**响应**:

```json
{ "success": true }
```

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 401 | 未登录 |
| 500 | 删除失败 |

---

### POST /api/courses/[id]/share

**描述**: 生成课程分享链接。若已存在则返回现有 token

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |

**响应**:

| 字段 | 类型 | 说明 |
|------|------|------|
| token | string | 分享 token |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 401 | 未登录 |
| 500 | 创建 token 失败 |

---

### DELETE /api/courses/[id]/share

**描述**: 删除课程分享链接

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |

**响应**:

```json
{ "success": true }
```

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 401 | 未登录 |

---

### POST /api/courses/fork

**描述**: 通过分享 token 复制课程到当前用户账户，包括大纲节点（保留父子关系）

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| token | string | 是 | 分享 token |

**响应**:

| 字段 | 类型 | 说明 |
|------|------|------|
| course_id | string | 新创建的课程 UUID |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 缺少 token |
| 401 | 未登录 |
| 404 | token 无效或课程不存在 |
| 500 | 复制大纲失败（会回滚已创建的课程） |

---

## 2. 大纲操作

### GET /api/courses/[id]/outline

**描述**: 获取课程全部大纲节点，按 order 排序

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |

**响应**:

| 字段 | 类型 | 说明 |
|------|------|------|
| (数组) | `OutlineNode[]` | 大纲节点数组 |
| id | string | 节点 UUID |
| course_id | string | 所属课程 |
| parent_id | string \| null | 父节点 ID |
| title | string | 节点标题 |
| type | string | 类型（chapter / topic / knowledge_point） |
| content | string \| null | 节点内容描述 |
| order | number | 排序序号 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 401 | 未登录 |
| 500 | 查询失败 |

---

### PUT /api/courses/[id]/outline

**描述**: 批量替换大纲节点（原子操作：删除旧节点 + 插入新节点，通过 RPC 函数 `upsert_outline_nodes`）。支持乐观锁冲突检测

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |
| nodes | `ParsedOutlineNode[]` | 是 | 树形大纲节点数组 |
| version | string | 否 | 乐观锁版本号（courses.updated_at），不匹配则返回 409 |

**响应**:

| 字段 | 类型 | 说明 |
|------|------|------|
| count | number | 插入的节点数量 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 409 | 版本冲突，课程已被其他会话修改 |
| 500 | RPC 执行失败 |

---

### POST /api/outline-nodes

**描述**: 创建单个大纲节点，自动计算排序序号

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| course_id | string | 是 | 所属课程 UUID |
| title | string | 是 | 节点标题 |
| type | string | 是 | 节点类型 |
| parent_id | string | 否 | 父节点 ID |
| content | string | 否 | 节点内容 |

**响应**: 返回创建的节点对象（status 201）

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 缺少必填字段 |
| 401 | 未登录 |
| 500 | 插入失败 |

---

### PATCH /api/outline-nodes/[id]

**描述**: 更新大纲节点，仅允许更新 title / content / type / parent_id / order

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 节点 UUID |
| title | string | 否 | 新标题 |
| content | string | 否 | 新内容 |
| type | string | 否 | 新类型 |
| parent_id | string | 否 | 新父节点 |
| order | number | 否 | 新排序 |

**响应**: 返回更新后的节点对象

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 没有有效的更新字段 |
| 401 | 未登录 |
| 500 | 更新失败 |

---

### DELETE /api/outline-nodes/[id]

**描述**: 删除大纲节点（数据库 CASCADE 自动删除子节点）

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 节点 UUID |

**响应**:

```json
{ "success": true }
```

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 401 | 未登录 |
| 500 | 删除失败 |

---

## 3. 学习系统

### GET /api/courses/[id]/lessons

**描述**: 获取课程所有课时，按 order 排序

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |

**响应**: 课时对象数组

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 401 | 未登录 |
| 500 | 查询失败 |

---

### POST /api/courses/[id]/lessons

**描述**: 为所有尚未生成课时的知识点批量生成课时内容（逐个串行调用 AI 以避免限流）

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 是（`generateLesson`，DashScope Qwen）

**maxDuration**: 60s

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |

**响应**:

| 字段 | 类型 | 说明 |
|------|------|------|
| count | number | 成功生成的课时数 |
| total | number | 需要生成的课时总数 |
| message | string | 若全部已生成，返回提示信息 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 没有知识点 |
| 401 | 未登录 |
| 404 | 课程不存在 |

---

### POST /api/courses/[id]/lessons/generate-one

**描述**: 为单个知识点生成带交互检查点的课时。支持两种模式：SSE 流式（`stream=true`）和阻塞式

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 是（`generateLessonOutline` + `generateSingleLessonChunk`，DashScope Qwen）

**maxDuration**: 60s

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |
| knowledge_point_id | string | 是 | 知识点节点 UUID |
| stream | boolean | 否 | 是否使用 SSE 流式传输 |

**SSE 事件流**（`stream=true` 时返回 `text/event-stream`）:

| 事件名 | 数据 | 说明 |
|--------|------|------|
| outline | `{ total_chunks, outline }` | 大纲阶段完成 |
| lesson | `{ lesson_id }` | 课时记录已创建 |
| chunk | `{ chunk_index, content, checkpoint_type, ... }` | 单个分块生成完成 |
| done | `{ lesson_id, chunks_generated }` | 全部完成 |
| error | `{ message }` | 出错 |

**阻塞式响应**:

| 字段 | 类型 | 说明 |
|------|------|------|
| lesson_id | string | 课时 UUID |
| chunks_generated | number | 生成的分块数 |
| outline | object[] | 课时大纲 |
| cached | boolean | 如果课时已存在则为 true |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 缺少 knowledge_point_id |
| 401 | 未登录 |
| 404 | 课程或知识点不存在 |
| 500 | 生成失败 |

---

### GET /api/courses/[id]/lessons/[lessonId]/chunks

**描述**: 获取课时分块内容。若数据库无分块记录，则按 `## ` 标题自动拆分课时内容作为 fallback

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |
| lessonId | string (URL) | 是 | 课时 UUID |

**响应**: 分块对象数组

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 分块 ID |
| lesson_id | string | 所属课时 |
| chunk_index | number | 分块序号 |
| content | string | Markdown 内容 |
| checkpoint_type | string \| null | 检查点类型 |
| checkpoint_prompt | string \| null | 检查点题目 |
| checkpoint_answer | string \| null | 检查点答案 |
| checkpoint_options | object \| null | 检查点选项 |
| key_terms | string[] \| null | 关键术语 |
| widget_code | string \| null | 交互组件代码 |
| remediation_content | string \| null | 补救内容 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 401 | 未登录 |
| 500 | 查询失败 |

---

### POST /api/courses/[id]/lessons/[lessonId]/progress

**描述**: 更新课时学习进度。完成课时时自动将对应知识点掌握度从 "unseen" 提升为 "exposed"

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |
| lessonId | string (URL) | 是 | 课时 UUID |
| completed | boolean | 否 | 是否完成 |
| lastChunkIndex | number | 否 | 最后阅读的分块序号 |
| checkpointResults | object | 否 | 检查点作答结果 |

**响应**:

```json
{ "ok": true }
```

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 401 | 未登录 |
| 404 | 课时不存在或不属于该课程 |
| 500 | 更新失败 |

---

### POST /api/attempts

**描述**: 提交答题记录。根据题目类型自动判分：选择题精确匹配，填空题模糊匹配，简答题关键词覆盖率 >= 50%。提交后返回正确答案和解析

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| question_id | string | 是 | 题目 UUID |
| user_answer | string | 是 | 用户答案 |

> 请求体经 `attemptCreateSchema`（Zod）校验

**响应**（status 201）:

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 答题记录 UUID |
| user_id | string | 用户 ID |
| question_id | string | 题目 ID |
| user_answer | string | 用户提交的答案 |
| is_correct | boolean | 是否正确 |
| correct_answer | string | 正确答案（提交后才显示） |
| explanation | string \| null | 题目解析 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 参数校验失败 |
| 401 | 未登录 |
| 404 | 题目不存在 |
| 500 | 插入失败 |

---

### PATCH /api/study-tasks/[id]

**描述**: 更新学习任务状态

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 任务 UUID |
| status | string | 是 | 新状态，只能是 `"todo"` 或 `"done"` |

**响应**: 返回更新后的任务对象

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | status 值无效 |
| 401 | 未登录 |
| 500 | 更新失败 |

---

### GET /api/courses/[id]/mastery

**描述**: 获取当前用户对课程各知识点的掌握度

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |

**响应**: 掌握度记录数组

| 字段 | 类型 | 说明 |
|------|------|------|
| concept_id | string | 知识点 UUID |
| current_level | string | 掌握等级（unseen / exposed / practiced / proficient / mastered） |

**错误码**: 无（未登录或查询失败均返回空数组）

---

### GET /api/courses/[id]/mistake-patterns

**描述**: 获取错题模式分析，按知识点聚合错误率，按错误率降序排列

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |

**响应**: 错题模式数组

| 字段 | 类型 | 说明 |
|------|------|------|
| kp_id | string | 知识点 UUID |
| kp_title | string | 知识点标题 |
| total_attempts | number | 总答题次数 |
| wrong_attempts | number | 错误次数 |
| error_rate | number | 错误率（0-1） |
| unique_questions | number | 涉及的不同题目数 |
| last_wrong_at | string \| null | 最近一次答错时间 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 401 | 未登录 |

---

### GET /api/courses/[id]/exams

**描述**: 获取课程的考试日期列表，按考试日期排序

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |

**响应**: 考试日期对象数组

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 考试记录 UUID |
| course_id | string | 课程 UUID |
| title | string | 考试名称 |
| exam_date | string | 考试日期 |
| knowledge_point_ids | string[] | 考试范围内的知识点 ID 列表 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 401 | 未登录 |
| 500 | 查询失败 |

---

### POST /api/courses/[id]/exams

**描述**: 创建考试日期记录

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |
| title | string | 是 | 考试名称 |
| exam_date | string | 是 | 考试日期 |
| knowledge_point_ids | string[] | 否 | 考试范围知识点 ID 列表 |

**响应**: 返回创建的考试日期对象（status 201）

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 缺少 title 或 exam_date |
| 401 | 未登录 |
| 500 | 插入失败 |

---

### DELETE /api/courses/[id]/exams

**描述**: 删除考试日期记录

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| exam_id | string | 是 | 考试记录 UUID |

**响应**:

```json
{ "success": true }
```

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 401 | 未登录 |

---

## 4. 内容生成

### POST /api/courses/[id]/generate

**描述**: 为课程生成学习任务。清除之前的自动生成任务和题目，基于大纲知识点重新生成学习任务（每次最多处理 5 个知识点以控制在 Vercel 60s 超时内）

**认证**: 需要

**Rate Limit**: 有（每门课程 30 秒内限 1 次）

**AI 调用**: 是（`generateStudyTasks`，DashScope Qwen）

**maxDuration**: 60s

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |
| language | string | 否 | 生成语言（"zh" / "en"） |

**响应**:

| 字段 | 类型 | 说明 |
|------|------|------|
| tasks_generated | number | 生成的任务数 |
| questions_generated | number | 生成的题目数（此端点固定为 0） |
| study_targets_used | number | 使用的知识点数 |
| task_error | string | AI 调用失败时的错误信息（可选） |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 大纲中没有可用知识点 |
| 401 | 未登录 |
| 404 | 课程不存在 |
| 429 | 频率限制，生成已在进行中 |

---

### POST /api/courses/[id]/generate-questions

**描述**: 按需为课程知识点生成练习题。只为尚无自动生成题目的知识点生成，每次批量处理最多 5 个知识点

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 是（`generateQuestionsFromOutline`，DashScope Qwen）

**maxDuration**: 60s

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |

**响应**:

| 字段 | 类型 | 说明 |
|------|------|------|
| generated | number | 本次生成的题目数 |
| kps_covered | number | 本次覆盖的知识点数 |
| kps_remaining | number | 剩余未覆盖的知识点数 |
| message | string | 若全部知识点已有题目，返回提示 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 没有知识点 |
| 401 | 未登录 |
| 404 | 课程不存在 |
| 500 | AI 生成失败 |

---

### POST /api/courses/[id]/regenerate

**描述**: 翻译大纲到目标语言并重新生成全部任务、题目和课时。会清除现有的学习任务、自动生成的题目和课时

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 是（Qwen qwen3.5-plus 翻译 + `generateStudyTasks` + `generateQuestionsFromOutline`）

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |
| language | string | 是 | 目标语言（"zh" 或 "en"） |

**响应**:

| 字段 | 类型 | 说明 |
|------|------|------|
| translated_nodes | number | 翻译的节点数 |
| tasks_generated | number | 生成的任务数 |
| questions_generated | number | 生成的题目数 |
| language | string | 目标语言 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 没有知识点 |
| 401 | 未登录 |
| 404 | 课程不存在 |

---

### POST /api/courses/[id]/extract

**描述**: 从上传的文件（PDF/图片）中提取教学内容，包括章节摘要、关键概念、公式，并匹配到课程知识点

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 是（Qwen qwen-plus-latest，结构化输出）

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |
| storagePath | string | 是 | 文件在 Supabase Storage 中的路径 |

**响应**:

| 字段 | 类型 | 说明 |
|------|------|------|
| sections | object[] | 提取的章节数组 |
| sections[].title | string | 章节标题 |
| sections[].summary | string | 2-3 句摘要 |
| sections[].key_concepts | string[] | 关键概念列表 |
| sections[].formulas | string[] | 数学公式列表 |
| sections[].matched_knowledge_point | string \| null | 匹配到的知识点标题 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 缺少 storagePath |
| 401 | 未登录 |
| 404 | 文件不存在 |

---

### POST /api/parse

**描述**: 解析教学大纲或考试文件。支持三种输入方式：纯文本大纲、文件大纲（PDF/图片）、考试试卷

**认证**: 需要

**Rate Limit**: 有（每用户每分钟 10 次）

**AI 调用**: 是（`parseSyllabus` / `parseSyllabusText` / `parseExamQuestions`，DashScope Qwen）

**maxDuration**: 60s

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| rawText | string | 条件必填 | 纯文本大纲内容（与 storagePath 二选一） |
| storagePath | string | 条件必填 | 文件存储路径（与 rawText 二选一） |
| parseType | string | 否 | 解析类型：`"syllabus"`（默认）或 `"exam"` |
| courseId | string | 否 | 课程 UUID（exam 模式下用于匹配知识点） |
| language | string | 否 | 输出语言偏好 |

**响应**:

| 字段 | 类型 | 说明 |
|------|------|------|
| type | string | `"syllabus"` 或 `"exam"` |
| data | object | 解析结果（大纲树形结构或题目数组） |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 缺少输入参数或无效 parseType |
| 401 | 未登录 |
| 429 | 频率限制 |
| 500 | AI 解析失败或文件下载失败 |

---

### POST /api/courses/[id]/chat

**描述**: 课程 AI 助手对话。基于课程大纲和知识点提供流式回复

**认证**: 需要

**Rate Limit**: 有（每用户每分钟 20 条消息）

**AI 调用**: 是（Qwen qwen3.5-plus，流式输出）

**maxDuration**: 30s

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |
| messages | UIMessage[] | 是 | 对话消息数组（ai SDK 格式） |

**响应**: `text/event-stream` 流式消息响应（ai SDK UIMessage 格式）

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 401 | 未登录 |
| 429 | 消息频率限制 |

---

### POST /api/courses/[id]/exam-prep

**描述**: 根据考试范围文本生成针对性练习题。从文本中提取考点，每个考点生成 2 道题目（批量并行，最多处理 12 个考点）

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 是（Qwen qwen3.5-plus，多轮调用）

**maxDuration**: 60s

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |
| scope_text | string | 是 | 考试范围描述文本 |

**响应**:

| 字段 | 类型 | 说明 |
|------|------|------|
| topics_found | number | 从文本中提取的考点数 |
| topics_processed | number | 实际处理的考点数 |
| questions_generated | number | 生成的题目总数 |
| topics_failed | string[] | 生成失败的考点列表 |
| topics | string[] | 提取的全部考点 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 缺少 scope_text 或未提取到考点 |
| 401 | 未登录 |
| 500 | 考点提取失败 |

---

### GET /api/courses/[id]/exam-scope

**描述**: 获取课程知识点列表（用于手动选择考试范围）

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |

**响应**: 知识点数组

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 知识点 UUID |
| title | string | 知识点标题 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 401 | 未登录 |

---

### POST /api/courses/[id]/exam-scope

**描述**: AI 解析考试范围文本，自动匹配到课程的知识点 ID

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 是（Qwen qwen3.5-plus）

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |
| scope_text | string | 是 | 考试范围描述文本 |

**响应**:

| 字段 | 类型 | 说明 |
|------|------|------|
| matched_kp_ids | string[] | 匹配到的知识点 UUID 列表 |
| matched_kp_titles | string[] | 匹配到的知识点标题列表 |
| total_kps | number | 课程总知识点数 |
| matched_count | number | 匹配到的知识点数 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 缺少 scope_text 或没有知识点 |
| 401 | 未登录 |
| 500 | AI 解析失败 |

---

### GET /api/courses/[id]/export-anki

**描述**: 导出课程题目为 Anki 可导入的 TSV 格式文件

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |

**响应**: `text/plain` 文件下载（Tab 分隔：front / back / tags）

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 没有可导出的题目 |
| 401 | 未登录 |

---

### POST /api/preview/learning

**描述**: 预览 AI 生成的学习任务和练习题（用于课程创建流程中的预览步骤）

**认证**: 需要

**Rate Limit**: 有（每 IP/用户每分钟 10 次）

**AI 调用**: 是（`generateStudyTasks` + `generateQuestionsFromOutline`，并行调用）

**maxDuration**: 60s

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 课程标题 |
| nodes | ParsedOutlineNode[] | 是 | 树形大纲节点数组 |

**响应**:

| 字段 | 类型 | 说明 |
|------|------|------|
| tasks | object[] | 生成的学习任务数组 |
| questions | object[] | 生成的练习题数组 |
| study_targets_used | number | 使用的知识点/叶节点数 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 缺少 title 或 nodes |
| 401 | 未登录 |
| 429 | 频率限制 |

---

## 5. 文件管理

### POST /api/upload

**描述**: 上传文件到 Supabase Storage（私有桶 `course-files`）。若提供 courseId，同时在 uploads 表创建记录

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**（FormData）:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 上传的文件 |
| courseId | string | 否 | 关联的课程 UUID |

**响应**:

| 字段 | 类型 | 说明 |
|------|------|------|
| storagePath | string | 文件在 Storage 中的路径 |
| fileName | string | 原始文件名（无 courseId 时） |
| fileType | string | 文件类型分类（pdf / ppt / image / text / other） |
| upload | object | uploads 表记录（有 courseId 时） |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 未提供文件 |
| 401 | 未登录 |
| 500 | 上传失败或数据库插入失败 |

---

### GET /api/courses/[id]/uploads

**描述**: 获取课程的上传文件列表，包含 1 小时有效期的签名下载 URL

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |

**响应**: 上传记录数组（附加 `download_url` 字段）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 上传记录 UUID |
| course_id | string | 课程 UUID |
| file_url | string | Storage 路径 |
| file_name | string | 原始文件名 |
| file_type | string | 文件类型 |
| status | string | 处理状态（pending / done） |
| parsed_content | object \| null | AI 提取结果 |
| download_url | string \| null | 签名下载 URL（1 小时有效） |
| created_at | string | 上传时间 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 401 | 未登录 |
| 500 | 查询失败 |

---

### DELETE /api/courses/[id]/uploads

**描述**: 删除上传文件（同时从 Storage 和数据库中删除）

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |
| upload_id | string | 是 | 上传记录 UUID |

**响应**:

```json
{ "success": true }
```

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 401 | 未登录 |

---

## 6. 笔记系统

### POST /api/courses/[id]/notes

**描述**: 创建课程笔记

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |
| (body) | object | 是 | 经 `noteCreateSchema` 校验的笔记数据 |

> 具体字段由 `noteCreateSchema` 定义

**响应**:

| 字段 | 类型 | 说明 |
|------|------|------|
| note | object | 创建的笔记对象 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 参数校验失败 |
| 401 | 未登录 |
| 404 | 课程不存在或不属于当前用户 |
| 500 | 插入失败（可能是 course_notes 表不存在） |

---

### POST /api/courses/[id]/notes/organize

**描述**: AI 整理笔记内容。分析笔记文本并匹配到课程知识点，支持指定知识点和追问答案

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 是（`organizeStudyNote`，DashScope Qwen）

**maxDuration**: 60s

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 课程 UUID |
| transcript | string | 是 | 笔记原始文本 |
| knowledge_point_id | string | 否 | 指定关联的知识点 UUID |
| clarification_answers | object | 否 | 追问问题的回答 |

> 请求体经 `noteOrganizeSchema` 校验

**响应**:

| 字段 | 类型 | 说明 |
|------|------|------|
| note | object | AI 整理后的笔记 |
| note.matched_knowledge_point_id | string \| null | 匹配到的知识点 UUID |
| note.matched_knowledge_point_title | string \| null | 匹配到的知识点标题 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 参数校验失败 |
| 401 | 未登录 |
| 404 | 课程不存在或不属于当前用户 |

---

## 7. 辅助功能

### GET /api/bookmarks

**描述**: 获取当前用户收藏的题目列表，包含题目详情和所属课程信息

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**: 无

**响应**: 收藏记录数组

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 收藏记录 UUID |
| note | string \| null | 用户备注 |
| created_at | string | 收藏时间 |
| questions | object | 题目详情（含 courses 嵌套） |
| questions.id | string | 题目 UUID |
| questions.stem | string | 题干 |
| questions.type | string | 题目类型 |
| questions.options | object \| null | 选项 |
| questions.answer | string | 正确答案 |
| questions.explanation | string \| null | 解析 |
| questions.difficulty | number | 难度 |
| questions.course_id | string | 课程 UUID |
| questions.courses.title | string | 课程标题 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 401 | 未登录 |
| 500 | 查询失败 |

---

### POST /api/bookmarks

**描述**: 收藏题目（已收藏则更新备注）

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| question_id | string | 是 | 题目 UUID |
| note | string | 否 | 收藏备注 |

**响应**: 返回收藏记录（status 201）

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 缺少 question_id |
| 401 | 未登录 |
| 500 | 插入/更新失败 |

---

### DELETE /api/bookmarks

**描述**: 取消收藏题目

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| question_id | string | 是 | 题目 UUID |

**响应**:

```json
{ "success": true }
```

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 401 | 未登录 |
| 500 | 删除失败 |

---

### GET /api/questions

**描述**: 获取课程题目列表（打乱顺序以实现交错练习）。不返回答案和解析，需通过提交答题记录获取

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| courseId | string (query) | 是 | 课程 UUID |

**响应**: 题目数组（随机排序）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 题目 UUID |
| course_id | string | 课程 UUID |
| source_upload_id | string \| null | 来源上传文件 ID |
| knowledge_point_id | string \| null | 关联知识点 ID |
| type | string | 题目类型（multiple_choice / fill_blank / true_false / short_answer） |
| stem | string | 题干 |
| options | object \| null | 选项数组 |
| difficulty | number | 难度（1-5） |
| created_at | string | 创建时间 |

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 缺少 courseId |
| 401 | 未登录 |
| 500 | 查询失败 |

---

### POST /api/questions

**描述**: 从上传的考试文件（PDF/图片）中解析并导入题目

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 是（`parseExamQuestions`，DashScope Qwen）

**maxDuration**: 60s

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| courseId | string | 是 | 课程 UUID |
| storagePath | string | 是 | 文件存储路径 |

**响应**: 返回插入的题目数组（status 201）

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 缺少 courseId 或 storagePath |
| 401 | 未登录 |
| 404 | 文件不存在 |
| 500 | 插入失败 |

---

### POST /api/questions/[id]/feedback

**描述**: 对题目提交反馈（每用户每题仅一条，重复提交覆盖）

**认证**: 需要

**Rate Limit**: 无

**AI 调用**: 否

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (URL) | 是 | 题目 UUID |
| reason | string | 是 | 反馈原因，必须是以下之一：`wrong_answer` / `unclear` / `too_easy` / `too_hard` / `duplicate` / `irrelevant` |

**响应**: 返回反馈记录

**错误码**:

| 状态码 | 含义 |
|--------|------|
| 400 | 无效的 reason 值 |
| 401 | 未登录 |
| 500 | 插入失败 |

---

## 通用说明

### 认证机制

所有端点使用 Supabase Auth，通过 Cookie 中的 session token 验证。未登录时统一返回 `401`：

```json
{ "error": "Unauthorized" }
```

### AI 模型

- **DashScope Qwen**（qwen3.5-plus / qwen-plus-latest）：通过 OpenAI 兼容 API 调用
- 基地址：`https://dashscope.aliyuncs.com/compatible-mode/v1`
- 需要 `DASHSCOPE_API_KEY` 环境变量

### Vercel 函数超时

- 涉及 AI 调用的端点设置 `maxDuration = 60`（秒）
- Chat 端点设置 `maxDuration = 30`（秒）
- 知识点处理数量受限以控制在超时范围内

### Rate Limiting

使用内存级别限流（`checkRateLimit`），服务器重启后重置：

| 端点 | 限制 |
|------|------|
| POST /api/courses/[id]/generate | 每课程 30s 内 1 次 |
| POST /api/courses/[id]/chat | 每用户每分钟 20 次 |
| POST /api/parse | 每用户每分钟 10 次 |
| POST /api/preview/learning | 每 IP 每分钟 10 次 |
