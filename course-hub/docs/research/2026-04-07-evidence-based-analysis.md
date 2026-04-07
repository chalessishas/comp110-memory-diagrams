# Evidence-Based Teaching Mechanisms → CourseHub 映射分析

**论文**: Evidence-based interactive teaching mechanisms for online learning
**分析日期**: 2026-04-07
**目的**: 逐条映射论文发现 → CourseHub 现有实现 → 识别缺口 → 给出优先级排序的行动建议

---

## 一、CourseHub 已正确实现的循证机制

### 1. 检索练习 Retrieval Practice（g = 0.50–0.61）⭐⭐⭐
**论文核心发现**: Rowland (2014) 159 个效应量 → g=0.50；STTT 组一周后回忆 61% vs SSSS 组 40%；自由回忆 > 简答 > 选择题

**CourseHub 实现**:
- `ChunkLesson.tsx`: 每个教学 chunk 强制包含 checkpoint（MCQ / fill_blank / open / code / latex）
- `review/page.tsx`: SRS 复习完全基于主动回忆，不是被动重读
- `generateSingleLessonChunk()` prompt: 明确要求每个 chunk 必须有 checkpoint
- **题型多样性**: MCQ + fill_blank + open + code + latex 覆盖从识别到产出的认知层次

**对齐度**: ★★★★★（核心架构完全对齐，且题型覆盖从 recognition 到 production）

### 2. 预测试 / 建设性失败 Pretesting + Productive Failure（d = 0.35–1.1, g = 0.36–0.58）⭐⭐⭐
**论文核心发现**: Richland et al. (2009) d=1.1 — 预测试即使答错也能显著增强后续学习；Kapur 的"建设性失败"在 STEM + 高中以上学生效果最强

**CourseHub 实现**:
- `ChunkLesson.tsx` 第 196-201 行: chunk_index===0 时先展示 checkpoint，后展示内容（pretest 模式）
- `generateSingleLessonChunk()` prompt: index===0 时注入特殊指令 `IMPORTANT: This is a PRETEST chunk`
- UI 第 207-209 行: 显示鼓励文案 "先试试看——答错没关系，尝试本身就能帮助学习"
- 第 343-349 行: pretest 提交后才显示教学内容，配 "现在来学习" 标签

**对齐度**: ★★★★★（直接实现了 Brilliant 的 problem-first 架构 + Kapur 的 productive failure）

### 3. FSRS 间隔重复（d = 0.54–0.85, FSRS 对 SM-2 99.6% 优势率）⭐⭐⭐
**论文核心发现**: 分布式练习 d=0.85（Donoghue & Hattie）；FSRS-6 使用 19 个机器学习参数、700M+ 评分训练；比 SM-2 减少 20-30% 复习量

**CourseHub 实现**:
- `spaced-repetition.ts`: 使用 ts-fsrs 5.3（论文讨论的同一算法）
- `getExamModeParams()`: 考试模式动态调整 `request_retention=0.95` + `maximum_interval=daysToExam`
- `getExamPriorityCards()`: 用 `get_retrievability(card, examDate)` 预测考试日记忆率，按升序排列
- 4 级评分 Again/Hard/Good/Easy 对应 FSRS 的 Rating enum

**对齐度**: ★★★★★（使用最先进的 SRS 算法，且有考试模式适配）

### 4. 生成效应 Generation Effect（d = 0.40–1.34）⭐⭐
**论文核心发现**: McCurdy et al. (2020) 延迟 >1 天时 d=1.34；开放式生成 > 限制式生成；甚至生成错误答案也有效

**CourseHub 实现**:
- `fill_blank` 题型: 强制学生从记忆中提取答案
- `open` 题型: 自由作答，最大化生成效应
- `code` / `latex` 题型: 产出型任务，不是识别型
- Pretest chunk: 在没学之前就要求生成答案（对齐 Kornell et al. 2009 "生成错误答案也有效"）

**对齐度**: ★★★★☆（题型覆盖好，但缺少 teach-back 机制）

### 5. 补救教学 Remediation Flow（部分对齐 Refutation Texts, g = 0.41）⭐⭐
**论文核心发现**: 错误概念必须与正确信息在记忆中**共激活**才能发生概念改变

**CourseHub 实现**:
- `ChunkLesson.tsx` 第 136-147 行: 答错 → 展示 remediation_content + remediation_question → 允许重试
- 最多 3 次尝试 → 超过后显示安慰文案 + "这个知识点会在复习中重新出现"
- 补救内容是 AI 生成的，针对同一概念的不同解释角度

**对齐度**: ★★★☆☆（有补救流程，但不是严格的 refutation text 格式 — 没有明确 "展示错误概念 → 标记为错误 → 解释正确概念" 三步结构）

### 6. 反填鸭设计 Anti-Cramming（论文 Part 4）⭐⭐
**论文核心发现**: 填鸭一周内遗忘 52%；间隔组仅遗忘 14%

**CourseHub 实现**:
- FSRS 算法天然强制间隔
- 考试模式 `maximum_interval=daysToExam` 限制最大间隔但不允许一次性刷完
- 无"一键显示答案"——必须作答后才能继续

**对齐度**: ★★★★☆（架构级反填鸭，但没有明确的 rate limiting / cooldown 像 Khan Academy 的 12 小时冷却期）

---

## 二、CourseHub 的循证缺口

### Gap 1: 无自适应难度（85% 规则）🔴 高优先级
**论文证据**: Wilson et al. (2019) Nature Communications — 最优错误率 ≈15.87%（准确率 ~85%）
- Duolingo 的 Birdbrain: 生成 200 候选题，选 14 道匹配学生水平
- Quizlet: 逻辑回归预测回忆概率，始终展示最弱项
- Khan Academy: 五级精通系统 + 掌握度可降级

**CourseHub 现状**: 所有学生同一课程看到完全相同的 checkpoint 题目。难度由 AI 生成时随机决定，无个体化。

**影响**: 对高水平学生太简单（无挑战 → 无学习），对低水平学生太难（认知过载 → 放弃）

### Gap 2: 无具体-抽象递进 Concreteness Fading 🟡 中等优先级
**论文证据**: Fyfe, McNeil & Borjas (2015) — concrete → representational → abstract 序列始终优于单一形式
- Goldstone & Son (2005): 大学生科学原理同样适用

**CourseHub 现状**: `generateSingleLessonChunk()` prompt 要求 "Include a concrete example" 但没有明确的三阶段递进结构。4 个 chunk 的顺序是 "foundation → application"，不是 "concrete → representational → abstract"。

### Gap 3: 无元认知校准 Metacognitive Calibration 🟡 中等优先级
**论文证据**: 最低表现四分位组过度自信最严重；元认知训练 g=0.57
- 学生对再读材料的信心最高（4.8/7）但表现最差

**CourseHub 现状**: 无置信度追踪。学生做题时不需要预判 "我觉得我能答对吗"。无校准反馈（"你在这个知识点上的预测准确率是 X%"）。

### Gap 4: 无变式理论 Variation Theory 🟡 中等优先级
**论文证据**: Gick & Holyoak (1983) 两个类比例子远优于一个；Marton 的四种模式（对比、泛化、分离、融合）

**CourseHub 现状**: 每个知识点只生成一组 chunk + 一套题目。没有"同一概念、不同表面特征"的多个例子供对比。

### Gap 5: 无 teach-back 机制（g = 0.48–0.56）🟢 低优先级（考前不值得做）
**论文证据**: Kobayashi (2024) — 学习者**事先知道要教**时 g=0.48-0.56，不知道时 g≈0.00
- 必须在学习前就告知，不是学完后才要求

**CourseHub 现状**: 无"向系统解释"功能。`open` 题型接近但不等同——teach-back 要求的是对整个概念的重新组织表述，不是回答特定问题。

### Gap 6: 交错复习 Interleaving 不足（g = 0.42）🟢 低优先级
**论文证据**: Taylor & Rohrer (2010) 交错几乎翻倍测试分数（77% vs 38%, d=1.21）
- 但词汇学习中交错反而有害（g=-0.39）

**CourseHub 现状**: 复习页面按课程隔离。同一课程内的 SRS 卡片无交错——虽然 FSRS 的到期日天然产生一些交错，但没有刻意混合不同知识点。

### Gap 7: 双重编码不足 Dual Coding（g = 0.39–0.51）🟢 低优先级
**论文证据**: Noetel et al. (2022) 综合 g=0.51；Mayer 的时间邻近性原则 d=1.30
- 简化图 > 写实图（Butcher 2006）

**CourseHub 现状**: 内容纯文本 + LaTeX 数学公式。无图表、无动画、无可视化。Calculus II 的积分区域、级数收敛等概念特别适合可视化但目前没有。

### Gap 8: 无 wrong-answer-specific 反馈 🟢 低优先级
**论文证据**: Brilliant 对每个错误选项都有定制反馈（不是泛泛的 "不对"）

**CourseHub 现状**: `ChunkLesson.tsx` 第 318-322 行 — 答错显示 "不太对 — [正确答案]"，不分析为什么选了错误选项。

---

## 三、CourseHub 避免的反模式（论文 Part 4 验证）

| 反模式 | 论文量化危害 | CourseHub 是否避免？ |
|--------|-------------|---------------------|
| 学习风格 | Pashler 2008: 无证据；89% 教育者仍信 | ✅ 不做 VARK 分类 |
| 被动策略 | 重读 d=0.47 vs 测试 d=0.74 | ✅ 强制主动回忆，无纯阅读模式 |
| 填鸭 | 一周遗忘 52% | ✅ FSRS 天然间隔 |
| 破坏内在动机的游戏化 | 实物奖励 d=-0.40 | ✅ 无积分/徽章/排行榜（streak 是行为记录不是奖励） |
| 选择过载 | 4 条件齐备时 d=0.84-1.18 | ⚠️ 部分 — 课程大纲可能有很多知识点让新手困惑 |

---

## 四、优先级排序：考前 3 天 vs 考后

### 🔴 考前可做（4/7 → 4/10, 投入产出比最高）

#### Action 1: Prompt 优化 — 具体→抽象递进（2 小时，纯 prompt 改动）
修改 `generateSingleLessonChunk()` 的 prompt，明确要求 4 个 chunk 遵循：
1. chunk 0（pretest）: 用具体生活场景出题
2. chunk 1: 用具体数值例子教学
3. chunk 2: 引入符号化/公式化表述
4. chunk 3: 抽象应用 + 变式练习

**预期收益**: 对齐 concreteness fading（Fyfe et al. 2015），改善数学概念理解
**风险**: 低（仅改 prompt 文本，不改代码逻辑）

#### Action 2: Exam mode 复习加入跨知识点交错（1 小时）
`getExamPriorityCards()` 当前按可提取率纯升序排列。改为：不相邻两卡不同知识点（简单的贪心插入）。

**预期收益**: 对齐 interleaving（d=1.21 in math），Calculus II 的级数判别法等特别适合交错（"这题用比较判别法还是比值判别法？"）
**风险**: 低（纯排序逻辑，不影响 FSRS 调度）

#### Action 3: 置信度校准追踪（2 小时）
复习时在展示答案前加一步 "你觉得你能答对吗？"（高/中/低）。统计预测准确率，定期显示 "你在这个知识点上的校准准确率是 X%"。

**预期收益**: 对齐 metacognitive calibration（g=0.57），帮助学生识别 "以为会了其实不会" 的盲区
**风险**: 中（需要改 review/page.tsx UI + localStorage schema）

### 🟡 考后可做（系统性改进）

| 改进 | 工作量 | 论文支撑 | 预期效果 |
|------|--------|----------|----------|
| 自适应难度（IRT 或简化版） | 1 周 | 85% rule + Birdbrain | 高 — 个体化学习路径 |
| Wrong-answer-specific 反馈 | 3 天 | Brilliant teardown | 中 — 更精准的概念纠正 |
| Teach-back "向 AI 解释" | 2 天 | g=0.48-0.56 | 中 — 深层理解 |
| 变式理论多例子 | 3 天 | Gick & Holyoak | 中 — 远迁移能力 |
| 双重编码（Manim/可视化） | 1 周+ | g=0.39-0.51 | 中 — 但工程量大 |
| Refutation text 三步结构 | 1 天 | g=0.41 | 低 — 现有补救已有效 |
| FSRS → Supabase 迁移 | 3 天 | FSRS paper | 中 — 跨设备 + 数据分析 |

---

## 五、论文三大结论 vs CourseHub 架构对齐

### 结论 1: "每次交互都应要求检索，不是识别"
> CourseHub: ✅ 核心架构对齐。Chunk-Checkpoint 交错确保每一步都有检索。Pretest 先于教学。SRS 复习完全基于主动回忆。

### 结论 2: "难度必须自适应且对专业水平敏感"
> CourseHub: ⚠️ 部分对齐。FSRS 的间隔是自适应的（基于个人记忆曲线），但题目难度不是自适应的。这是最大缺口。

### 结论 3: "学习感受与实际学习负相关，产品必须主动对抗"
> CourseHub: ✅ 架构级对齐。Pretest 让学生先失败再学习；SRS 逼学生复习已遗忘材料；无"跳过复习"按钮。但缺少元认知校准来让学生意识到自己的偏差。

---

## 六、一句话总结

CourseHub 在检索练习、预测试、FSRS、生成效应四大高效应量机制上达到了产品级实现（对齐 Brilliant + Anki/FSRS 的最佳实践）。最大的单点缺口是**自适应难度**——论文、Duolingo、Khan Academy、Quizlet 四方证据都指向"85% 成功率"是最优学习区间，CourseHub 目前对所有学生展示相同内容。考前 3 天的最高 ROI 改进是 prompt 层面的 concreteness fading + 复习交错 + 置信度校准。
