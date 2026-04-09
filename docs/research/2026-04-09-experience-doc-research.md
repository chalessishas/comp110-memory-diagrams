# Experience Doc 改进调研

> 调研日期: 2026-04-09
> 目标: 为 docs/experience.md 寻找改进方向

---

## 一、Lessons Learned / Postmortem 文档最佳实践

### 1. Google SRE 的 Blameless Postmortem 文化
- **来源**: [Google SRE Book - Postmortem Culture](https://sre.google/sre-book/postmortem-culture/)
- **核心洞察**: 有效的 postmortem 把重点从"谁的错"转向"系统哪里让人做了错误决策"。关键发现：action items 不被跟踪是重复事故的首要原因。Google 要求每个 action item 有 owner + deadline + 完成追踪。
- **对我们的价值**: 我们的 experience.md 记录了"坑"但没有跟踪"修复状态"。33 条里哪些已经有防护措施、哪些还在裸奔，看不出来。

### 2. Pragmatic Engineer: Postmortem 时机与结构
- **来源**: [Incident Review and Postmortem Best Practices](https://blog.pragmaticengineer.com/postmortem-best-practices/)
- **核心洞察**: 最佳时机是事件后 24-72 小时。文档必须包含：影响范围、根因分析(Five Whys)、时间线、action items。发布给更广团队可以帮助其他人避免同样的坑。
- **对我们的价值**: 我们的条目缺少"根因分析"层——大多停在"发生了什么"，没有深入"为什么会发生"。Five Whys 方法可以直接采用。

### 3. Action Item 完成率决定 Postmortem 价值
- **来源**: [Google SRE Workbook - Postmortem Culture](https://sre.google/workbook/postmortem-culture/), [Postmortem Action Items (USENIX)](https://sre.google/static/pdf/login_spring17_09_lunney.pdf)
- **核心洞察**: 不完整的 action items 让重复事故概率大增。组织应优先排期 postmortem 工作，跟踪完成率，给团队足够时间实施改进。
- **对我们的价值**: 我们第六节"AI 助手执行层面"的 5 条坑，至今仍在反复踩（编年忘写、技术决策请示）。说明光记录不够，需要执行层的防护机制。

---

## 二、AI 编码助手的持久记忆机制

### 4. Claude Code: CLAUDE.md + Auto Memory
- **来源**: [How Claude remembers your project](https://code.claude.com/docs/en/memory), [claude-memory-compiler](https://github.com/coleam00/claude-memory-compiler)
- **核心洞察**: CLAUDE.md 每次 session 加载到上下文。Auto memory 让 Claude 自动积累跨 session 知识（构建命令、调试心得、架构笔记）。最佳实践：单文件控制在 200 行以内，用 markdown headers 分组。社区项目 claude-memory-compiler 用 hooks 自动捕获 session 并提取关键决策。
- **对我们的价值**: 我们的 experience.md 已有 162 行，接近上限。需要考虑拆分或分层策略。

### 5. Cursor: .cursor/rules/ 多文件架构
- **来源**: [Cursor Rules Docs](https://docs.cursor.com/context/rules), [Mastering Cursor Rules](https://dev.to/pockit_tools/mastering-cursor-rules-the-ultimate-guide-to-cursorrules-and-memory-bank-for-10x-developer-alm)
- **核心洞察**: Cursor 从单文件 .cursorrules 演进到 .cursor/rules/*.mdc 多文件架构。每个规则文件可以指定触发条件（glob pattern），只在相关文件被编辑时注入上下文。还有 "Generate Memories" 功能自动记录用户偏好。
- **对我们的价值**: 按触发条件加载是好思路——做 GPU 训练时不需要看 CourseHub 的坑，反之亦然。我们可以按项目/领域拆分 experience 文件。

### 6. 开发者对 AI 助手记忆的核心诉求
- **来源**: [10 Things Developers Want from Agentic IDEs](https://redmonk.com/kholterhoff/2025/12/22/10-things-developers-want-from-their-agentic-ides-in-2025/)
- **核心洞察**: 开发者最不满的是"agent 每次 session 都忘记一切"。他们要求 agent 能记住过去的决策、识别之前项目的模式、保持项目历史感知。
- **对我们的价值**: 验证了 experience.md 的方向是对的——跨 session 的失败记忆是刚需。

---

## 三、工程团队失败学习的学术研究

### 7. Edmondson & Harvey (2025): 团队学习的组织框架
- **来源**: [Team Learning in the Field](https://journals.sagepub.com/doi/10.1177/10464964251316877) (Small Group Research, 2025)
- **核心洞察**: 新技术可能阻碍团队的反思性学习（reflexive learning）。团队学习行为受领导力、成员稳定性、反馈获取、目标模糊度等因素影响。
- **对我们的价值**: AI 助手每次新 session = "成员不稳定"，天然不利于反思学习。experience.md 正是弥补这个缺陷的机制。

### 8. 从失败中学习的三阶段模型
- **来源**: [Organizational Learning From Failure](https://www.researchgate.net/publication/321635342_Organizational_Learning_From_Failure_Present_Theory_and_Future_Inquiries)
- **核心洞察**: 从失败中学习包含三个阶段：(1) 失败识别 (2) 交互式意义建构 (3) 组织适应。仅仅记录失败（阶段1）不等于学习，必须经过分析和行为改变才算完成。
- **对我们的价值**: 我们的 experience.md 停在阶段1-2（记录+简单归因），缺少阶段3（验证行为是否真的改变了）。

---

## 四、改进建议

### 建议 1: 增加"防护状态"字段

每条 pitfall 加一个状态标记，表明是否已有防护措施：

```
### 14. Ollama blob hash 会变
**状态**: [已防护] _resolve_ollama_blob() 动态解析，无需手动干预_
```

```
### 31. 编年记录不写或延后补写
**状态**: [未防护] 仍依赖人工纪律，无自动检查机制
```

这直接解决 Google SRE 发现的"action items 不被跟踪"问题。季度清理时优先处理"未防护"条目。

### 建议 2: 按领域拆分为多文件，主文件保留索引

借鉴 Cursor 的多文件架构：

```
docs/experience/
  index.md          # 索引 + 通用条目（工作流、AI 助手执行）
  gpu-training.md   # GPU/云服务相关 (条目 5-8)
  ai-detector.md    # AI 检测器相关 (条目 9-23)
  coursehub.md      # CourseHub 相关 (条目 24-26)
```

好处：(1) 单文件不超过 200 行上限 (2) 做特定项目时只需加载相关文件 (3) 各项目独立维护，不互相干扰。主索引文件保留条目编号到子文件的映射。

### 建议 3: 每条加"根因层"(Five Whys)

当前格式只有"坑是什么"和"代价"。增加一个"根因"字段，用 Five Whys 追问到可操作的层面：

```
### 29. 听不懂模糊指代就去硬搜
**根因**: 收到模糊指令 → 没有先确认意图 → 直接用关键词搜索 → 搜不到就换关键词而非换策略
         → 根本原因：缺少"先理解再行动"的强制检查点
**防护**: [未防护] 需要在 CLAUDE.md 中加入"遇到模糊指令先用一句话确认理解"的规则
```

这把文档从"事故记录"升级为"根因知识库"，对应学术研究中"从阶段1到阶段3"的跨越。

---

## Sources

- [Google SRE Book - Postmortem Culture](https://sre.google/sre-book/postmortem-culture/)
- [Google SRE Workbook - Postmortem Culture](https://sre.google/workbook/postmortem-culture/)
- [Postmortem Action Items (USENIX)](https://sre.google/static/pdf/login_spring17_09_lunney.pdf)
- [Incident Review and Postmortem Best Practices - Pragmatic Engineer](https://blog.pragmaticengineer.com/postmortem-best-practices/)
- [How Claude remembers your project](https://code.claude.com/docs/en/memory)
- [claude-memory-compiler](https://github.com/coleam00/claude-memory-compiler)
- [Cursor Rules Docs](https://docs.cursor.com/context/rules)
- [Mastering Cursor Rules](https://dev.to/pockit_tools/mastering-cursor-rules-the-ultimate-guide-to-cursorrules-and-memory-bank-for-10x-developer-alm)
- [10 Things Developers Want from Agentic IDEs](https://redmonk.com/kholterhoff/2025/12/22/10-things-developers-want-from-their-agentic-ides-in-2025/)
- [Team Learning in the Field (Edmondson & Harvey, 2025)](https://journals.sagepub.com/doi/10.1177/10464964251316877)
- [Organizational Learning From Failure](https://www.researchgate.net/publication/321635342_Organizational_Learning_From_Failure_Present_Theory_and_Future_Inquiries)
