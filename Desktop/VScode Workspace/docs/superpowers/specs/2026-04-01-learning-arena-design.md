# 学习斗兽场（Learning Arena）— 产品设计文档

> 日期: 2026-04-01
> 状态: Draft
> 技术栈: Next.js 14 + Supabase + Claude API + Canvas LMS API

## 一句话

拍照或连接 Canvas → AI 识别知识点 → 匹配同类学习者 → AI 出题 PK 对战。

## 产品定位

面向所有学习者的知识竞技平台。用户上传学习内容（Canvas 大纲或拍照），AI 自动提取知识点并生成针对性题目，匹配学习相同知识点的用户进行实时或异步的答题对战。

**目标用户**: 通用（大学生 + 自学者）
**商业模式**: 产品化（免费基础对战 + 付费高级功能）
**差异化**: 市场上没有产品将「用户自有学习内容出题 + 知识点匹配 + ELO 对战」三者结合

## 核心数据流

```
Canvas 授权 → 拉取大纲 → AI 提取知识点 → 匹配对手 → AI 出题 → PK 对战 → ELO 结算
                                ↑
拍照上传 ──────────────────────┘ (补充入口)
```

## 系统架构

### 四大模块

#### 1. 数据导入层
- **Canvas 导入 (主要)**: 用户粘贴 Canvas API Token + 学校 URL → 自动拉取所有课程大纲
- **拍照上传 (补充)**: 多模态 LLM 直接识别图片内容，提取知识点
- **手动输入 (兜底)**: 用户手动输入学习主题

Canvas 导入的优势：一次授权覆盖所有课程，知识点归类天然一致（同一门课的学生看同一份大纲），比拍照更准确。

#### 2. AI 引擎
- **知识点提取**: Claude API 解析大纲/图片 → 输出结构化知识点列表
- **标签标准化**: 统一命名空间（如 `linear-algebra/eigenvalues`），确保不同用户的同一知识点能匹配
- **自动出题**: 根据知识点生成选择题（4 选 1），支持 easy/medium/hard 三档难度
- **出题 prompt 策略**: 题目必须测试理解而非记忆，干扰项需要合理（常见错误概念），题干清晰无歧义

#### 3. 匹配 + 对战

**匹配算法** (参考 LearnClash):
- 30% ELO 相近度
- 30% 课程重叠
- 40% 知识点重叠

**对战模式**:

| 模式 | 触发条件 | 机制 | 技术 |
|------|---------|------|------|
| 实时 PK | 对手在线 | 倒计时 15s/题，5 题，实时看对方进度 | Supabase Broadcast + Presence |
| 异步挑战 | 对手离线 | 推送通知，24h 内作答，超时算弃权 | Supabase DB + 通知 |

**对战状态机**:
```
发起挑战 → AI 生成 5 题 → 等待对手
  ├─ 对手在线 → 实时 PK → 双方答完 → 结算 ELO
  └─ 对手离线 → 异步挑战 → 对手 24h 内答题 → 结算 ELO
```

**ELO 计算**: 标准 ELO 公式，K=32（新用户 K=64 加速定位），初始分 1000。

**实时对战技术细节**:
- 答题动作通过 Supabase Broadcast 低延迟传输（不经 DB）
- Presence 跟踪双方在线状态
- 答题结果写入 DB 后通过 Broadcast 再推送，绕过 Postgres Changes 延迟
- Supabase Free 层 200 并发连接，支撑约 100 场并发 PK

#### 4. 用户系统
- **Auth**: Supabase Auth（Google OAuth 登录）
- **学习档案**: 已导入课程、知识点覆盖率、强弱项分析
- **对战历史**: 对战记录、胜率、ELO 变化曲线
- **排行榜**: 全局 + 按知识点/课程分类

## 数据模型

### profiles
| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid (FK → auth.users) | 主键 |
| display_name | text | 显示名 |
| avatar_url | text | 头像 |
| canvas_token | text (encrypted) | Canvas API Token，加密存储 |
| canvas_url | text | 学校 Canvas URL |
| elo_rating | int (default: 1000) | ELO 积分 |
| total_wins | int | 总胜场 |
| total_losses | int | 总败场 |

### courses
| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid | 主键 |
| user_id | uuid (FK → profiles) | 所属用户 |
| canvas_course_id | text | Canvas 课程 ID |
| name | text | 课程名（如 "STOR 120"） |
| syllabus_raw | text | 原始大纲文本 |
| imported_at | timestamptz | 导入时间 |

### topics
| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid | 主键 |
| course_id | uuid (FK → courses) | 所属课程 |
| name | text | 知识点名称（如 "特征值与特征向量"） |
| normalized_tag | text | 标准化标签（如 "linear-algebra/eigenvalues"） |
| difficulty_estimate | int (1-5) | 预估难度 |
| source | text | 来源（"canvas" / "photo" / "manual"） |

### battles
| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid | 主键 |
| topic_id | uuid (FK → topics) | 对战知识点（MVP: 单知识点，后续可扩展为多知识点混合） |
| challenger_id | uuid (FK → profiles) | 发起者 |
| opponent_id | uuid (FK → profiles) | 对手 |
| status | text | "pending" / "active" / "done" |
| mode | text | "realtime" / "async" |
| winner_id | uuid | 胜者 |
| elo_change | int | ELO 变化值 |
| created_at | timestamptz | 创建时间 |
| finished_at | timestamptz | 结束时间 |

### questions
| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid | 主键 |
| battle_id | uuid (FK → battles) | 所属对战 |
| topic_id | uuid (FK → topics) | 所属知识点 |
| question_text | text | 题目文本 |
| options | jsonb | 4 个选项 |
| correct_answer | text | 正确答案 (a/b/c/d) |
| difficulty | int (1-3) | 实际难度 |
| order_index | int | 题目顺序 |

### answers
| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid | 主键 |
| battle_id | uuid (FK → battles) | 所属对战 |
| question_id | uuid (FK → questions) | 所属题目 |
| user_id | uuid (FK → profiles) | 答题者 |
| selected_answer | text | 用户选择 |
| is_correct | boolean | 是否正确 |
| time_taken_ms | int | 用时（毫秒） |
| answered_at | timestamptz | 答题时间 |

### RLS 策略
- profiles: 用户只能读写自己的 profile，其他用户的 display_name/avatar/elo 可读
- courses/topics: 用户只能读写自己的，但 normalized_tag 供匹配系统查询
- battles: 参与者双方可读写
- questions/answers: 对战参与者可读，答题者可写自己的 answer
- canvas_token: 仅用户自己可读，服务端函数可用

## MVP Phase 1 范围（2-3 周）

### 包含
- Supabase Auth（Google 登录）
- Canvas Token 手动粘贴 + 课程大纲导入
- AI 知识点提取（Claude API）
- 发现同知识点用户列表
- 异步挑战（发起 → AI 出 5 题 → 双方答题 → ELO 结算）
- 基础排行榜（全局 + 按知识点）
- 移动端适配（响应式设计）

### 不包含（Phase 2+）
- Canvas OAuth（先用 token 粘贴，验证核心体验后再做 OAuth）
- 实时对战（Supabase Broadcast）
- 拍照上传入口
- 知识图谱 + 学习弱项分析
- 推送通知
- 虚拟货币/道具系统
- 反作弊机制

## 页面结构

```
/                → Landing page（产品介绍 + CTA）
/login           → Google OAuth 登录
/dashboard       → 主面板（我的课程、最近对战、推荐对手）
/courses         → 课程管理（Canvas 导入、知识点浏览）
/arena           → 斗兽场（发起挑战、查看挑战、对战列表）
/battle/[id]     → 对战页面（答题界面）
/battle/[id]/result → 对战结果（得分对比、ELO 变化）
/leaderboard     → 排行榜（全局、按知识点筛选）
/profile/[id]    → 用户档案（对战历史、知识点分布）
/settings        → 设置（Canvas Token、通知偏好）
```

## 关键风险

1. **Canvas Token 安全**: 必须加密存储，Supabase Vault 或 pgcrypto，绝不能明文
2. **学校限制**: 部分学校可能禁止学生生成 API Token，需要实测 UNC 是否允许
3. **AI 出题质量**: 题目质量是核心体验的命门，需要精心设计 prompt + 人工验证样本
4. **知识点标准化一致性**: 不同大纲描述同一知识点的方式不同，AI 标签可能不一致导致匹配失效
5. **冷启动**: 初期用户少时匹配困难，异步模式 + AI 对手（bot）作为兜底
6. **Supabase Free 层限制**: 200 并发连接、500MB 数据库、1GB 存储，MVP 够用但需要监控

## 竞品参考

| 产品 | 借鉴点 |
|------|--------|
| Kahoot | 竞答 + 实时排名的用户粘性 |
| Quizizz | 异步竞赛模式解决冷启动 |
| StudyGlen/Quizgecko | 拍照出题的可行性验证 |
| LearnClash | ELO + 知识点重叠的混合匹配算法 |
| Gimkit | 虚拟经济系统提升留存（Phase 2+） |
