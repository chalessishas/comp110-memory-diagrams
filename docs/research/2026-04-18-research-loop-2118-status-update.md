# Research Loop Status Update

**时间**: 2026-04-18 21:18
**触发**: Research Loop（自动，每 60 分钟）
**目的**: 汇总当前三个待研究主题的状态，避免重复调研

---

## 主题一：arknights-sim P6 方向

**状态：已有完整调研，方向明确**

`arknights-2026-04-18-2113.md` 已完成 P6 完整调研：

| 坑 | 建议 | 优先级 |
|----|------|--------|
| AOE | `splash_radius: float` 欧氏半径，先不做 shape 枚举 | P6 首选 |
| Buff pipeline | `atk_ratio_buffs: list[float]` + `atk_multiplier_buffs: list[float]` 两阶段 | P6 首选 |
| Targeting 策略 | 优先级栈（blocked > special > aggro > path_progress） | P6 二选 |
| SP lockout | SP 满无目标时锁止（不触发、不消耗） | P6 二选 |
| Elevation | 已在 P3 隐式解决（range 平面覆盖） | 完成 |

**下一步执行（无需再调研）**：
1. `core/operator.py`：`atk_ratio_buffs + atk_multiplier_buffs` 替换 `_atk_bonus`
2. `core/entity.py`：`splash_radius: float = 0.0` + `apply_aoe(battle, target, dmg)`
3. `core/battle.py`：`_resolve_aoe_operators()` 调用 AOE 伤害分发
4. `tests/test_p6_aoe.py` + `tests/test_p6_buff.py`：至少 8 个新测试

---

## 主题二：TOEFL iBT 2026 格式

**状态：已确认，无需行动**

`toefl-2026-reading-format.md` 结论：ETS 官方确认 Reading 维持 2 passages × ~700 words。早先研究报告的"200-word adaptive"是误报（来自非官方论坛）。

**待用户决策**：当前代码是否需要将题目长度从旧格式更新到 2024+ 新格式（listening section 减为 2 conversions）。Listening 部分有精简，Reading 无变化。

---

## 主题三：comp110-redesign Phase 2

**状态：Phase 1 交付完成，Phase 2 等待启动指令**

Phase 1（6 文件，~74KB）已锁定交付。CS50 Duck 调研发现：
- 纯苏格拉底追问（"你觉得原因是什么？"）对弱基础学生产生挫败感
- **建议三级提示**：L1=苏格拉底（追问） / L2=引导提示（给方向） / L3=直接答案
- Phase 2 实现时，AI TA 组件应支持 `hint_level: 1|2|3` 状态机

**待用户行动**：将 Phase 1 设计稿交给 DeepSeek/Cursor 作为 context，指定 Next.js 15 + Tailwind v4 实现。

---

## 优先推荐

**当前最高价值行动**：实现 arknights-sim P6（AOE + buff pipeline）

理由：
- P1-P5 全部完成（27 tests passing），代码质量高
- P6 技术细节已研究完毕，不需要再做调研
- 能把 tests 从 27 扩展到 35+，证明 AOE/buff 机制正确性
- 其他项目（Signal-Map / ai-text-detector）均在等待用户提供密钥，非阻塞工作
