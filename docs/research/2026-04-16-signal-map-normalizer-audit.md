# Signal-Map Normalizer 静态审计（Pitfall #5 建筑匹配率 74%）

**时间**：2026-04-16 19:14
**触发**：Progress Loop 切出 TOEFL 后对 Signal-Map 做积压审计（该项目最后 commit 距今 2 周）
**范围**：静态代码审查 `src/lib/ingest/normalizer.ts`，不访问生产 DB、不改代码
**目标**：识别把匹配率从 74% 往上推的具体改进点

---

## 核心发现

### F1. 文档 vs 代码漂移 ⚠️
- **Signal-Map/CLAUDE.md** 明确描述："建筑匹配：缩写前缀 → 60%+ token 重叠 → **Haversine <500m** → null fallback"
- **实际代码 (normalizer.ts:160)**：`let bestDist = 100; // max 100 meters`
- 文档说 500m，代码执行 100m。这是典型的"文档领先于现实 / 现实领先于文档"——不确定哪个是 ground truth。
- **影响**：如果代码 100m 是设计意图、文档错写 500m → 需修文档。如果 500m 是目标、100m 是过严的实际 → 一行改 `bestDist = 500` 可能提升匹配率，但引入 5× FP 风险（UNC 主校区 500m 半径内通常 5+ 栋建筑）。

### F2. 短字符串子串匹配的 FP 风险
第 26 行：`if (sSimple.includes(cSimple) || cSimple.includes(sSimple)) return 1;`

- 无最小长度 guard
- 如果 building name / alias 里有单词 "hall"（长度 4），它会 return 1（满分）匹配**所有带 hall 的 event location**
- 类似的短词 risk：`lab`, `gym`, `park`, `cafe`, `hub`
- 应加 guard：`if (cSimple.length < 5) skip 子串反向匹配`

### F3. ABBREVIATIONS 和 DIRECT_MAPPINGS 规模有限
- `ABBREVIATIONS`：10 条（gl/dey/ch/sa/su/mh/gb/fd/mas/pcm）
- `DIRECT_MAPPINGS`：14 条（含错别字、非正式名、子空间）
- UNC 86 栋建筑 + 5 数据源，每源有独特的称呼习惯。10+14 条显然远远不够覆盖 26% unmatched 的长尾
- **根因**：扩展这两个映射表**依赖手工发现**。目前没有自动化"把 unmatched 的 locationText 聚类统计"的管道

### F4. Token matching 的拼写变体盲区
第 34-38 行用 `st.includes(ct) || ct.includes(st)`，只处理子串，不处理编辑距离。
- "Phillip" vs "Phillips" → `phillip.includes('phillips')` = false，反向也 false，需要 tokens 其他 hits 到 60% 才救得回
- "Kenan" vs "Kenen"（打字错）→ 无救
- "UL" vs "Undergraduate Library" → 无救（abbreviation 表里没有）

### F5. 多地点 location 文本无拆分
目前 `locationText` 被当成单字符串传入，如果事件文本是 "Phillips 215 / Sitterson 102" 或 "Kenan Stadium (rain: Carmichael)"：
- 当前逻辑会把整个字符串去 fuzzy match，两个建筑都不会匹配到 0.6+
- 应该先 `/ [\/\(;,] /` 拆分，每段独立 resolve，保留第一个成功

### F6. 100m Haversine 只 fallback 到坐标，不叠加到文本结果
当文本 resolve 失败但有 lat/lng，strategy 2 生效。**但** 当文本有**弱匹配**（比如 0.55）且坐标能覆盖同一栋建筑，目前会被文本分数拒绝（<0.6）、坐标也可能漏（>100m）。两个弱信号没有叠加机制。

---

## 按 ROI 排序的建议改进

| # | 改进 | 成本 | 风险 | 预期匹配率提升 | 依赖 |
|---|---|---|---|---|---|
| A | **加 no-match logging**：resolveBuildingId 返回 undefined 时写入 `IngestLog`，记录 locationText + source + timestamp | ~8 行 | 低 | 0% 即时，但解锁**数据驱动扩表** | 无 |
| B | **子串匹配最小长度 guard**（F2）：`if (cSimple.length < 5) 跳过 substring return 1` | ~2 行 | 低（可能让 1-2 个真实"Hall/Lab"-only 事件变 unmatched，但这类事件本就是 low-quality location） | 降低 FP，不直接提升匹配率 | 无 |
| C | **拆分多地点 location 文本**（F5）：`locationText.split(/\s*[\/\;]\s*/)` 每段独立 resolve | ~10 行 | 低 | +1–3% | 无 |
| D | **Haversine 扩到 500m + 弱文本 0.4 叠加**（F1 + F6）：若文本分 ≥0.4 且坐标 ≤500m 指向同一建筑，判定匹配 | ~15 行 | **中**（500m 内多建筑，需实测 FP） | +3–5% | 需跑一次 ingest 对比 |
| E | **基于 A 的数据扩 DIRECT_MAPPINGS**（F3）：积累 1 周 no-match 日志后，人工或 GPT 批量归类高频 locationText | ~50 行扩表 | 低 | +5–10%（长尾） | A 必须先上 + 1 周数据 |
| F | **token 编辑距离 ≤2 允许**（F4）：用 Levenshtein ≤2 作为次级匹配信号 | ~20 行 | 中（可能引入 FP） | +1–2% | 无 |

**推荐顺序**：A → B → C → （数据积累一周后） E → D → F

理由：
- A 零风险但解锁后续所有数据驱动改动
- B 清理潜在的 FP 债（当前代码可能在"虚增" matchrate）
- C 立即吃到多地点事件的 easy win
- E 是最大 ROI 但需要 A 打下数据基础
- D 风险中但增益明显，靠数据决定
- F 是最小边际，最后做

---

## 下一步命令

1. **（本周内，主人操作）** 确认 F1 漂移的 ground truth：CLAUDE.md 500m 是旧设计，还是代码 100m 是过紧？如果主人说 500m 是对的 → 加进改进 D 的权重。
2. **（agent 可自主，30 行）** 实施改进 A + B + C，三合一 commit。加 no-match 日志只写不读，B 只加最小长度 guard，C 只拆分字符串——三者互不耦合、均低风险。
3. **（一周后）** 跑 `SELECT locationText, COUNT(*) FROM IngestLog WHERE matched = false GROUP BY locationText ORDER BY count DESC LIMIT 50` 看长尾，按出现频次更新 DIRECT_MAPPINGS。
4. **（可选，主人定）** 把 normalizer 从规则匹配升级为小模型语义匹配（类似 TOEFL 项目今日 Research Loop 考虑的 LLM 路径）——26% 长尾 × 日活 × building click conversion 才能算出 ROI 是否值得。

---

## 不在本次审计范围内的事

- 没跑生产 DB，没查真实 unmatched 样本（需要 `DATABASE_URL` 授权和网络访问）
- 没验证"匹配率 74%"这个数字的出处——可能是主人人工抽样，可能是某次 ingest 日志统计。应该先确认测量口径
- 没跑 `npm run ingest` 本地重现 unmatched 分布——需要有 `.env` 里的 token 且 5 个 parser 能正常拉数据，风险是本地机器意外触发生产写入

## 元规律

今天 session 的元模式：**auto Progress Loop 被 TOEFL 阻塞后（主人需绿灯 LLM 路径），自然转向最久未动的项目做 audit**。这个 "分布式维护" 行为是 auto loop 的优势——持续在多项目之间寻找最小 ROI 正的改动，而不只是在单一项目里挖地三尺。但前提是**audit 成本远低于实施**，否则只是在换项目继续挤 gap。
