# Learning Arena (学习斗兽场) 产品调研

> 调研日期：2026-04-01
> 产品概念：拍照上传学习内容 -> AI 识别知识点 -> 匹配同类用户 -> AI 出题 PK 对战
> 技术栈：Next.js + Supabase

---

## 一、类似产品案例

### 1.1 Kahoot! — 课堂实时竞答先驱

- **URL**: https://kahoot.com/
- **核心发现**: Kahoot! 将测验变成了竞技运动，支持教师创建题目、学生实时抢答。2025 年推出 AI Notes Scanner，可以将手写笔记扫描后自动生成 Kahoot 题目。但其 PDF 问题生成器要求 PDF 文本可复制/编辑，纯图片扫描 PDF 不支持。
- **对项目的价值**: 验证了「竞答 + 实时排名」模式的用户粘性极高。AI 笔记扫描功能与我们的拍照出题概念高度重合，可参考其交互设计。
- **局限性**: Kahoot 是教师驱动的（教师出题 -> 学生答题），不是学生驱动的自主 PK 模式。没有按知识点匹配对手的机制。OCR 对纯图片支持有限。

### 1.2 Quizizz — 自节奏竞答 + 游戏化

- **URL**: https://play.google.com/store/apps/details?id=com.quizizz_mobile
- **核心发现**: 结合了 Kahoot 的参与感和自节奏功能，学生可以按自己的速度完成测验同时保留游戏元素。支持异步竞赛模式。
- **对项目的价值**: 异步模式值得借鉴——不要求双方同时在线也能 PK（先答的人成绩作为挑战目标）。这解决了匹配时在线用户不足的冷启动问题。
- **局限性**: 没有拍照出题功能，题库依赖手动创建或平台内容。

### 1.3 StudyGlen — 拍照 OCR + AI 出题

- **URL**: https://studyglen.com/quiz
- **核心发现**: 目前市面上少数支持图片输入 + OCR 的 AI 出题工具。支持 PDF/文本/图片输入，生成多选、判断、简答题，支持 13 种语言，有免费层。通过 OCR 扫描手写笔记或教科书页面生成测验。
- **对项目的价值**: 最接近「学习斗兽场」拍照出题环节的竞品。证明了 OCR -> 出题链路的可行性。但它是单人学习工具，没有对战功能。
- **局限性**: 纯工具型产品，无社交/竞技层。出题质量依赖 OCR 准确率，复杂公式/图表识别可能不佳。

### 1.4 Quizgecko — 手机拍照秒出测验

- **URL**: https://quizgecko.com/
- **核心发现**: AI 驱动的测验生成平台，移动端支持用手机摄像头扫描文字或上传文档，转换为多种题型（多选、判断、填空、匹配、简答）。有 iOS 和 Android 原生 App。
- **对项目的价值**: 移动端拍照出题的完整产品参考。证明了手机摄像头 -> AI 出题的用户体验是通畅的。
- **局限性**: 同样是单人学习工具，无竞技/社交维度。免费额度有限。

### 1.5 Quiz Battle (Apple App Store)

- **URL**: https://apps.apple.com/us/app/quiz-battle/id6468363489
- **核心发现**: 专注于知识竞赛对战的 App，玩家之间进行实时问答 PK。
- **对项目的价值**: 验证了 Quiz PK 作为独立产品形态的市场存在。但题目是平台预设的通识类题目，不是基于用户自有学习内容生成的。
- **局限性**: 题库固定，不支持用户自定义内容；通识类竞赛与学科学习场景差距大。

### 1.6 LearnClash — ELO 积分竞技学习

- **URL**: https://learnclash.com/
- **核心发现**: 将 ELO 评分系统应用于学习竞赛，通过匹配分数计算（30% ELO 相近度 + 30% 类别重叠 + 40% 话题重叠）进行智能匹配。题目难度根据段位自动缩放，所有 rating 变化持久化记录。
- **对项目的价值**: 匹配算法的直接参考。ELO + 知识点重叠的混合匹配策略正是「学习斗兽场」需要的核心机制。
- **局限性**: 内容方向偏通识竞赛，不是「拍照上传自有学习资料」的模式。

### 1.7 Gimkit — 游戏秀式课堂学习

- **URL**: https://www.jotform.com/blog/gamification-apps-for-education/
- **核心发现**: 复刻游戏秀体验，学生在设备上答题赚取虚拟货币，正确答案奖励金币。将经济系统引入学习。
- **对项目的价值**: 虚拟经济/货币系统是很好的留存机制，可以考虑在斗兽场中加入积分/金币/道具系统。
- **局限性**: 依赖教师创建内容，课堂场景限定。

---

## 二、Supabase Realtime 实时对战技术实现

### 2.1 Supabase Realtime 三大能力

- **URL**: https://supabase.com/docs/guides/realtime
- **核心发现**: Supabase Realtime 提供三种机制：
  1. **Broadcast** — 低延迟的客户端间消息推送，fire-and-forget，不经过数据库。适合游戏事件、答题动作。
  2. **Presence** — 跟踪和同步用户在线状态。适合显示对战房间中的在线玩家。
  3. **Postgres Changes** — 监听数据库变更并推送。适合排行榜更新、答题结果持久化后通知。
- **对项目的价值**: 三种机制组合使用可以覆盖实时对战的全部需求。Broadcast 传输答题动作（低延迟），Presence 显示在线状态，Postgres Changes 同步持久化数据。
- **局限性**: Postgres Changes 在高写入频率（数百次/秒）下延迟可达 500ms-1s；单线程处理导致计算资源升级对性能提升有限。

### 2.2 延迟性能基准

- **URL**: https://supabase.com/docs/guides/realtime/benchmarks
- **核心发现**:
  - **Broadcast**: 极低延迟，消息不经过数据库，直接 WebSocket 转发。
  - **Postgres Changes**: 低频写入（2-3次/秒）延迟 <200ms，用户无感知；高频写入（数百次/秒）延迟 500ms-1s。
  - **优化方案**: 可以先写数据库，再通过 Broadcast 重新推送给客户端，绕过 Postgres Changes 的延迟瓶颈。
- **对项目的价值**: Quiz PK 场景答题频率不高（每人每题 5-30秒），Postgres Changes 的延迟完全可接受。但倒计时同步、即时反馈等场景应该用 Broadcast。
- **局限性**: 文档中的基准测试不一定反映真实网络环境下的端到端延迟。

### 2.3 完整实现案例：Vercel + Supabase 实时多人 Quiz

- **URL**: https://dev.classmethod.jp/en/articles/vercel-supabase-realtime-multiplayer-quiz-game/
- **核心发现**: 使用 Next.js 16 (App Router) + React 19 + TypeScript + Supabase 构建。数据库设计包含 6 张表：photos、rooms、room_players、room_questions、votes、vote_counts。通过 RLS 阻止客户端直接访问敏感数据，投票聚合通过 Broadcast 广播。自定义 hooks：`useRoom`（订阅游戏状态）、`useVoteCounts`（订阅投票计数）、`usePresence`（显示在线玩家）。
- **对项目的价值**: 技术栈完全吻合（Next.js + Supabase），可以直接参考其数据库设计和 Realtime 订阅模式。6 张表的设计可以直接映射到斗兽场的房间/玩家/题目/答案结构。
- **局限性**: 这是投票类 Quiz 而非知识竞赛 PK，答题逻辑和评分机制不同。

### 2.4 SupaQuiz — 开源 Supabase Quiz 游戏

- **URL**: https://github.com/yallurium/supaquiz
- **核心发现**: 开源的多人问答游戏，基于 Supabase 构建。可以直接查看源码学习实现细节。
- **对项目的价值**: 直接可用的开源参考，可以 fork 后修改。
- **局限性**: 需要检查维护状态和代码质量。

### 2.5 Next.js + Supabase 无后端实时多人游戏

- **URL**: https://dev.to/iakabu/i-built-a-real-time-multiplayer-browser-game-with-supabase-nextjs-no-backend-server-required-h28
- **核心发现**: 证明了 Next.js + Supabase 可以在无独立后端服务器的情况下构建实时多人游戏。完全 serverless 架构。
- **对项目的价值**: 验证了不需要额外后端即可实现实时对战的架构可行性，降低运维复杂度。
- **局限性**: 无后端意味着反作弊逻辑需要放在 Supabase Edge Functions 或 RLS 中，实现相对受限。

### 2.6 连接数与价格

- **URL**: https://supabase.com/docs/guides/realtime/pricing
- **核心发现**:
  - **Free 层**: 200 并发 Realtime 连接，消息数量无限
  - **Pro 层**: $10 / 1000 peak connections，$2.50 / 100万条消息
  - API 请求和消息本身在 Free 层不限量，只限并发连接数
- **对项目的价值**: 200 并发连接 = 100 场同时进行的 1v1 对战，对 MVP 和早期用户足够。如果每场 PK 持续 3 分钟，每小时可支撑 ~2000 场对战。
- **局限性**: 用户规模增长后需要付费；如果做观战功能，连接数会成倍增长。

---

## 三、AI 从图片识别知识点并自动出题

### 3.1 多模态 LLM 方案（GPT-4o / Claude / Gemini）

- **URL**: https://www.leewayhertz.com/gpt-4-vision/
- **核心发现**: 2025-2026 年的多模态大模型（GPT-4o、Claude 3.5、Gemini 2.0）可以直接接受图片输入，理解图中的文字、公式、图表、手写内容，并与学科知识关联。不再需要单独的 OCR 步骤——VLM 本身具备 OCR 能力。研究表明多模态 LLM 在图像内容分析上可以与专用框架竞争甚至超越。
- **对项目的价值**: 一步到位的方案——直接将拍照图片发送给多模态 LLM，让它同时完成「识别内容 + 提取知识点 + 生成题目」。链路最短，实现最简单。
- **局限性**: API 调用成本较高（图片 token 消耗大）；延迟 2-5 秒；对极潦草的手写或低质量拍照可能识别不准。

### 3.2 OCR + LLM 两步方案

- **URL**: https://photes.io/blog/ocr-research-trend
- **核心发现**: 2026 年 OCR 技术已经从传统方法全面转向 AI/LLM 驱动。开源 OCR 模型（如 PaddleOCR、EasyOCR、Tesseract 5）可以先提取文字，再由 LLM 理解内容并生成题目。开源 VLM 在 2025 年将推理成本降低了 60%，同时在 MMBench 上达到 >80% 的分数。
- **对项目的价值**: 两步方案可以降低成本——OCR 步骤用免费/低成本模型，只在出题步骤调用付费 LLM。也可以缓存 OCR 结果复用。
- **局限性**: 两步链路增加延迟和复杂度；OCR 错误会传导到出题质量；公式/图表类内容需要专门的 OCR 模型。

### 3.3 开源 VLM 方案

- **URL**: https://www.bentoml.com/blog/multimodal-ai-a-guide-to-open-source-vision-language-models
- **核心发现**: 2025-2026 年开源 VLM 快速成熟（Qwen2-VL、InternVL2、LLaVA-Next 等），推理成本比商用模型低 60%，可自部署。适合高频调用场景。
- **对项目的价值**: 如果用户量大、API 成本敏感，可以自部署开源 VLM 降低单次调用成本。
- **局限性**: 需要 GPU 服务器（A100/H100），自部署运维复杂度高；模型质量仍略逊于 GPT-4o/Claude。

### 3.4 GPT-4V 教育场景研究

- **URL**: https://arxiv.org/html/2405.07163
- **核心发现**: 研究论文证实 GPT-4V 能够正确理解任意给定的图片，并将图片内容与学科知识和教学法关联。在 Visual Question Answering (VQA) 教育场景中表现良好。
- **对项目的价值**: 学术层面验证了「图片 -> 学科知识点识别 -> 出题」链路的可行性。GPT-4V 不仅能识别图片内容，还能理解其教育语境。
- **局限性**: 研究场景多为标准教材图片，用户随手拍的歪斜、模糊照片的表现未被充分测试。

### 3.5 现有产品的实现路径

- **URL**: https://quizgecko.com/mobile
- **核心发现**: Quizgecko 的实际产品流程：手机拍照 -> OCR 提取文字 -> AI 生成多种题型。已经有数十万用户验证了这条路径。GPT Quiz Generator for Forms 也支持类似功能，直接集成到 Google Forms。
- **对项目的价值**: 产品层面的可行性已被市场验证。关键差异在于我们加上了对战层。
- **局限性**: 这些产品的出题质量参差不齐，特别是在专业学科领域。

---

## 四、ELO 匹配系统

### 4.1 ELO 评分算法

- **URL**: https://www.geeksforgeeks.org/dsa/elo-rating-algorithm/
- **核心发现**: ELO 算法由 Arpad Elo 于 1960 年为美国国际象棋联合会开发，根据胜负动态调整数值评分。核心公式简单：预期胜率 = 1 / (1 + 10^((Rb-Ra)/400))，实际得分与预期得分的差值乘以 K 系数更新 rating。被 League of Legends、Overwatch、Valorant、CS 等游戏广泛采用。
- **对项目的价值**: 算法简单成熟，可以直接用于斗兽场的段位系统。按知识领域分别维护 ELO 值（数学 ELO、物理 ELO 等），实现精细匹配。
- **局限性**: 纯 ELO 不考虑知识领域匹配；新用户 rating 不稳定（冷启动问题）。

### 4.2 混合匹配策略（LearnClash 案例）

- **URL**: https://learnclash.com/blog/elo-rating-system
- **核心发现**: LearnClash 的匹配公式：30% ELO 相近度 + 30% 类别重叠 + 40% 话题重叠。每次 rating 变化都记录历史，支持成长曲线可视化。题目难度与段位挂钩。
- **对项目的价值**: 这个匹配权重分配可以直接借鉴。对于学习斗兽场，可以调整为：30% ELO + 30% 学科匹配 + 40% 具体知识点重叠（基于拍照上传内容的 AI 标签）。
- **局限性**: 需要足够的在线用户才能实现高质量匹配；知识点标签的准确性直接影响匹配质量。

---

## 五、对产品设计的具体建议

### 5.1 核心流程建议

基于调研，推荐以下产品流程：

```
拍照/上传 -> 多模态 LLM 一步处理 -> 知识点标签 + 题目生成 -> 匹配对手 -> 实时 PK -> 结算 & ELO 更新
```

**为什么选择一步 LLM 方案而非 OCR + LLM 两步**：
- 2026 年多模态 LLM 的图片理解能力已经足够好，不需要单独 OCR
- 一步方案链路更短，出错点更少
- 可以理解图表/公式的语义，不仅仅是文字
- 成本可以通过缓存和批处理优化

### 5.2 数据库设计建议（参考 Vercel+Supabase Quiz 案例）

```
users          — 用户基础信息 + 各学科 ELO rating
materials      — 用户上传的学习材料（图片 URL + AI 提取的知识点标签 + 生成的题目缓存）
rooms          — 对战房间（状态机：waiting -> playing -> finished）
room_players   — 房间内玩家（关联 user + room）
room_questions — 房间内题目（从 materials 缓存中抽取）
answers        — 玩家答题记录（答案 + 耗时 + 是否正确）
elo_history    — ELO 变化记录（支持成长曲线展示）
```

### 5.3 Supabase Realtime 使用策略

| 场景 | 使用机制 | 原因 |
|------|---------|------|
| 匹配成功通知 | Broadcast | 低延迟，不需要持久化 |
| 对手答题状态（已答/未答） | Broadcast | 即时反馈，fire-and-forget |
| 倒计时同步 | Broadcast | 需要毫秒级同步 |
| 房间在线状态 | Presence | 内置断线检测 |
| 答题结果 & 分数 | Postgres Changes | 需要持久化，延迟 <200ms 可接受 |
| 排行榜更新 | Postgres Changes | 低频更新，延迟无关 |

### 5.4 冷启动解决方案

调研发现的关键风险是**匹配时在线用户不足**。建议：

1. **异步挑战模式**（学 Quizizz）：先答的人成绩作为挑战目标，后答的人异步 PK。不要求同时在线。
2. **AI 对手**：匹配超时 10 秒后自动匹配 AI 对手，AI 答题速度和准确率根据用户 ELO 动态调整。
3. **题目池共享**：用户 A 拍照生成的题目，经审核后可以被其他学同一科目的用户使用，形成 UGC 题库。

### 5.5 成本控制

- **图片识别 + 出题**：GPT-4o 每次调用约 $0.01-0.03（取决于图片大小）。100 个用户每天上传 3 张照片 = $3-9/天。
- **缓存策略**：一张照片生成的题目缓存起来，多次 PK 复用。只在题目用完时重新生成。
- **Supabase Free 层**：200 并发连接，早期完全够用。

### 5.6 差异化竞争点

基于调研，现有产品的空白地带正是学习斗兽场的机会：

| 现有产品 | 有什么 | 缺什么 |
|---------|-------|-------|
| Kahoot/Quizizz | 实时竞答 | 学生自主出题、拍照识别 |
| StudyGlen/Quizgecko | 拍照出题 | 对战、社交、排名 |
| Quiz Battle | PK 对战 | 自定义内容、学科匹配 |
| LearnClash | ELO 匹配 | 拍照出题、用户生成内容 |

**学习斗兽场 = 拍照出题 + 知识点匹配 + ELO 对战**，目前没有产品将这三者结合。

### 5.7 MVP 功能优先级

| 优先级 | 功能 | 工期估算 |
|--------|------|---------|
| P0 | 拍照 -> AI 出题（单人模式） | 3-5 天 |
| P0 | Supabase 用户系统 + 题目存储 | 2 天 |
| P1 | 1v1 实时匹配 + PK | 5-7 天 |
| P1 | ELO 积分系统 | 2-3 天 |
| P2 | 异步挑战模式 | 3 天 |
| P2 | 排行榜 + 成长曲线 | 2 天 |
| P3 | AI 对手 | 2-3 天 |
| P3 | 题目池 UGC 共享 | 3-5 天 |

建议 MVP 先做 P0 + P1（约 2 周），验证「拍照出题」和「实时 PK」两个核心假设。

---

## Sources

- [Kahoot! AI Tools](https://support.kahoot.com/hc/en-us/articles/17152945038355-How-to-use-Kahoot-AI-tools)
- [Quizizz (Wayground)](https://play.google.com/store/apps/details?id=com.quizizz_mobile)
- [StudyGlen AI Quiz Generator](https://studyglen.com/guides/best-ai-quiz-generator)
- [Quizgecko Mobile App](https://quizgecko.com/mobile)
- [Quiz Battle App](https://apps.apple.com/us/app/quiz-battle/id6468363489)
- [LearnClash ELO Rating System](https://learnclash.com/blog/elo-rating-system)
- [Gimkit Gamification](https://www.jotform.com/blog/gamification-apps-for-education/)
- [Supabase Realtime Docs](https://supabase.com/docs/guides/realtime)
- [Supabase Realtime Benchmarks](https://supabase.com/docs/guides/realtime/benchmarks)
- [Supabase Realtime Pricing](https://supabase.com/docs/guides/realtime/pricing)
- [Vercel + Supabase Multiplayer Quiz](https://dev.classmethod.jp/en/articles/vercel-supabase-realtime-multiplayer-quiz-game/)
- [SupaQuiz (GitHub)](https://github.com/yallurium/supaquiz)
- [Next.js + Supabase No Backend Game](https://dev.to/iakabu/i-built-a-real-time-multiplayer-browser-game-with-supabase-nextjs-no-backend-server-required-h28)
- [Supabase Realtime Broadcast Docs](https://supabase.com/docs/guides/realtime/broadcast)
- [GPT-4 Vision Overview](https://www.leewayhertz.com/gpt-4-vision/)
- [OCR Technology 2026 Trends](https://photes.io/blog/ocr-research-trend)
- [Open-Source VLMs 2026](https://www.bentoml.com/blog/multimodal-ai-a-guide-to-open-source-vision-language-models)
- [GPT-4V VQA for Education (arXiv)](https://arxiv.org/html/2405.07163)
- [ELO Rating Algorithm](https://www.geeksforgeeks.org/dsa/elo-rating-algorithm/)
- [Supabase Realtime Guide (Cotera)](https://cotera.co/articles/supabase-realtime-guide)
- [Supabase Realtime Limits](https://supabase.com/docs/guides/realtime/limits)
