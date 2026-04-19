# Arknights Simulator — P8 候选方案评估

**时间**: 2026-04-18 22:23
**现状**: P7 完成，48/48 绿（targeting priority + SP lockout）

---

## 地形效果（Ground Effects）评估

### 官方机制（Terra Wiki）
- **Icy Surface**：造成 Cold（ASPD -30%），在冰面上持续生效；Frozen 敌人受到更高位移伤害
- **Oil Slick**：见于部分关卡，触碰后着火造成持续伤害
- **Environmental effects**：降雪（Snowfall）、Frigid 机制

### 实现成本
- Tile 状态追踪（每格独立状态）
- 单位 status effect 系统（Cold / Burn / Oil）
- Status → stat 修改 pipeline（Cold ASPD -30%）
- Event log 标注

**结论**：中高复杂度，主要服务于专项干员（冻结流），对核心战斗循环提升有限。当前 48 测试紧耦合，status effect 系统引入有回归风险。**暂不推荐作 P8。**

---

## P8 推荐候选（更简、价值更高）

### 候选 A：治疗型干员 HP 恢复（10–20 行）
**现状**：`attack_type="heal"` 已存在，但实战中 Medic 干员无法对友军生效（只打地方）
**实现**：`_resolve_operators()` 中 heal 类型干员寻找 HP 最低的友军而非敌方目标
**测试**：`test_healer_restores_ally_hp` × 2

### 候选 B：DP 费用系统（50–80 行）
**现状**：干员部署无费用限制
**实现**：`Operator.cost: int`，`Battle.dp: float`（每秒 +1），部署时扣除；0 dp 不能部署
**测试**：`test_dp_accumulates` / `test_insufficient_dp_blocks_deploy` × 3–4

### 候选 C：Stun / Slow 状态效果（30–50 行）
**现状**：无 debuff 系统
**实现**：`Entity.status_effects: list[StatusEffect]`，每 tick 消耗 duration；`Entity.effective_atk_interval()` 考虑 slow 倍率
**测试**：`test_stun_freezes_attack` / `test_slow_reduces_atkspd` × 4

---

## 优先级建议

**P8 = 候选 A（Healer）**，因为：
1. 实现成本最低（10–20 行），测试最简单（2 个测试）
2. 补完核心单位类型（目前 Medic 部署了但功能残废）
3. 不引入新的系统性复杂度

**P9 = 候选 B（DP）**，因为战略深度高，是正式 stage 设计的前提。

**P10 = 地形效果**，需要先有 status effect 基础设施（候选 C）再叠加地形触发。
