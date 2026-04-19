# Arknights-Sim: Targeting Priority + SP Lockout 调研

**时间**: 2026-04-18 21:29
**目标**: 评估两个剩余机制坑的实现方案，给出优先级和具体代码变更

---

## 结论先行

**优先级 1：SP Lockout（实现成本低，影响技能时序正确性）**
**优先级 2：Targeting Priority（影响 ranged 攻击目标选择）**

---

## SP Lockout

### 官方机制（Terra Wiki: Skill Point）

- Auto-recover 技能：SP 满 + 没有有效目标 → SP 冻结（橙色仪表），不再累积，技能不触发
- 有效目标出现 → 立即触发技能，SP 重置
- 区别于 cooldown（技能正在执行中）

### 当前代码问题

`operator.py:update_skill()` 中，SP 满了就立即触发技能，没有检查是否有目标：
```python
if self.sp >= self.skill.sp_cost:
    self.sp = 0.0
    self._skill_remaining = self.skill.duration
    if self.skill.on_start: self.skill.on_start(self)
    self._skill_just_fired = True
```

实际场景问题：SilverAsh 部署时无敌人（波次未到），20s 后 SP 满，技能在空目标时触发，浪费 15s 无效持续时间。

### 实现方案

**operator.py 变更**：
1. 新增字段 `_sp_locked: bool = field(init=False, default=False)`
2. `update_skill(self, dt, has_target: bool = True)` 新增参数（默认 True，向后兼容）
3. SP 满时，若 `not has_target`：锁定并 return；否则解锁并触发

**battle.py 变更**：
在 `_resolve_operators()` 中：将 `target = self._blocked_enemy(op)` 移到 `update_skill` 之前，并传入 `has_target=target is not None`

```python
# 原顺序（错误）:
op.update_skill(DT)
target = self._blocked_enemy(op)

# 新顺序（正确）:
target = self._blocked_enemy(op)
op.update_skill(DT, has_target=target is not None)
```

---

## Targeting Priority

### 官方机制（Terra Wiki: Aggression）

优先级栈（高到低）：
1. Blocked unit（被阻挡的敌人）
2. Special Priority（地图特殊规则）
3. Highest positive aggression
4. **Closest to destination（_path_progress 最大）**
5. Highest negative aggression

### 当前代码问题

`battle.py:_blocked_enemy()` ranged 分支：
```python
if op.attack_range == "ranged":
    for enemy in self.enemies:
        if enemy.alive:
            return enemy   # 返回列表中第一个活着的敌人，与生成顺序相关
```

### 实现方案

替换 ranged 分支为按 `_path_progress` 排序取最大值：
```python
if op.attack_range == "ranged":
    live = [e for e in self.enemies if e.alive]
    return max(live, key=lambda e: e._path_progress) if live else None
```

---

## 新增测试计划

### test_p7_sp_lockout.py
1. `test_sp_stops_at_cost_when_no_target` — 无目标时 SP 累积到 cost 后冻结
2. `test_skill_fires_when_target_appears` — 目标出现后立即触发
3. `test_sp_resumes_after_skill_ends` — 技能结束后 SP 重新累积
4. `test_has_target_true_fires_normally` — has_target=True 时技能正常触发（回归）

### test_p7_targeting.py
1. `test_ranged_targets_highest_path_progress` — ranged op 优先攻击 progress 最大的敌人
2. `test_targeting_ignores_dead_enemies` — 死亡敌人不进入候选
3. `test_melee_targeting_unchanged` — melee block 逻辑不受影响

---

## 风险

- SP Lockout 的 `has_target` 传递需要 `battle.py` 调用顺序调整；若顺序错误，会导致 skill log 时序偏移 1 tick
- Targeting 变更对现有 P3 测试（`test_heavy_requires_combined_arms`）有潜在影响：该测试依赖 Exusiai 攻击特定敌人，需运行回归确认
