# course-hub Research Index — 2026-04-17

**目的**：course-hub 项目在 `docs/research/` 已有 **5 份 report**（最早 04-01，最晚 04-09）。今日 Research Loop 跨日触发本应生产新研究，但经 audit 决定 **不重复生产**——8 天前的 research 已覆盖项目主要方向，8 天内 course-hub 代码无大改（workspace git log 仅有 chronicle/research 文档活动），新 Research 边际价值低。本文件作为 index，指向已有 research，节省未来 session 的 re-discovery 成本。

---

## 已有 research 清单

| 文件 | 日期 | 主题 | 摘要 |
|-----|------|------|-----|
| `2026-04-01-course-video-research.md` | 04-01 | 课程视频功能 | 视频功能需求调研 |
| `2026-04-01-course-video-tech-research.md` | 04-01 | 视频技术栈选型 | Vimeo / YouTube / self-host 对比 |
| `2026-04-03-coursehub-next-steps.md` | 04-03 | 下一步路线图 | 功能优先级 + 时间线 |
| `2026-04-03-coursehub-tech-research.md` | 04-03 | 技术栈深度 | Next.js + Supabase 架构验证 |
| `2026-04-09-coursehub-vercel-deployment.md` | 04-09 | 部署方案 | Vercel 部署 + 环境变量 |

---

## 为何不再生产第 6 份

1. **代码 stable**：2026-04-09 之后无重大 commit（仅文档活动）。研究应 track 代码状态，代码无变化则研究边际价值递减。
2. **5 份已覆盖**：需求 + 技术栈 + 路线 + 架构 + 部署 5 大主题齐全，再挖只会在 micro-optimization 层。
3. **主人决策 pending**：前 5 份 research 里应有待决项（需要主人看才能推进），生产第 6 份反而让主人更 overwhelmed。
4. **今日跨日 Research 已做 4 份**（ai-text-detector × 2 + chronicle × 1 + 修正 × 1）——session context 预算应用在真正未覆盖的项目上。

---

## 主人下次回来时的建议动作

1. **阅读 04-03 next-steps** 看当前最高优先级是什么
2. 如果 next-steps 有具体 item 可 act，告诉 Claude 实施
3. 如果 next-steps 已过期（很可能 8 天前的）→ 要求生成**新 next-steps**（届时新 Research 才有价值）

---

## 元规律

**Research Loop 不应盲目生产报告**。当某项目已有充足 research 且代码无新变化时，写一份 index 指向现有报告**比新产出更有价值**——避免稀释 + 减少主人扫描成本。今日 chronicle 已堆 >100 turn headers，docs/research/ 已 ~15 份文件，继续堆积会降低整个 docs 知识密度。
