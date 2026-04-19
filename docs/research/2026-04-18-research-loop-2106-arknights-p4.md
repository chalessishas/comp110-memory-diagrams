# Research Loop — 2026-04-18 21:06 — arknights-sim P4 状态审计

## 当前状态总结

### 已完成（有 commit）
| Phase | 内容 | 测试 |
|-------|------|------|
| P1 | Entity/Operator/Enemy/Battle 基础战斗 | 4/4 ✅ |
| P2 | Map/Stage loader/YAML 关卡/波次入场/路径行进 | 4/4 ✅ |

### 已实现但**未 commit**（git untracked/modified）
| Phase | 内容 | 测试 |
|-------|------|------|
| P4 | Skill 系统（SP 累积、激活、ATK buff、on_end 恢复） | 7/7 ✅ |

P4 实现文件：
- `core/skill.py` — Skill dataclass，SP cost/duration/mode/callbacks
- `core/operator.py` — 添加 `update_skill(dt)`, `skill_active`, `effective_atk()`, SP 累积逻辑
- `data/__init__.py`, `data/operators.py`, `data/enemies.py` — 工厂函数（SilverAsh S3、Arts Master）
- `tests/test_p4_skill.py` — 7 tests 全绿
- `examples/silver_ash_burst.py` — 演示脚本

**全套 15 tests（P1+P2+P4）均通过。**

### 尚未实现
| Phase | 内容 |
|-------|------|
| P3 | Elevation（远程干员可打过近战阻挡）、block_count 上限、多干员优先级 |
| P5 | CLI `python -m arknights_sim`、`--log json` 输出、完整 pytest 套件 |

---

## 下一步建议

### 方案 A：先 commit P4，再实现 P3（推荐）
理由：P4 代码已绿，长时间 untracked 有丢失风险。P3 补上 elevation/block 上限后，P5 CLI 是收尾层。

**P3 关键工作量：**
1. `Entity` 添加 `elevation: str = "ground"` / `"aerial"` 和 `attack_range: str = "melee"` / `"ranged"`
2. `Battle._blocked_enemy(op)` 改为：ranged op 可攻击任意活敌（无视阻挡），melee op 只攻击第一个阻挡目标
3. `Battle._blocking_operator(enemy)` 改为：计算各 op 已阻挡数，超出 `op.block` 则不算阻挡
4. 新增 `tests/test_p3_elevation.py`：Exusiai（ranged）+Hoshiguma（melee block=3）联合作战

估算工作量：~40 行代码 + 4-6 个测试。

### 方案 B：跳过 P3，直接 P5 CLI
理由：P5 是 DESIGN_BRIEF 终态，用户更可能用 CLI 跑演示而非关心 elevation 机制。
风险：P3 缺口（block 上限无限）是已知技术债，不修会在多干员场景出错。

---

## 技术风险
- `_cleanup_dead()` 当前对已到达目标的敌人不记录"defeated"日志（`_goal_reachers` 排除），这是正确行为，但如果用户查日志可能困惑。
- `_blocked_enemy` 仍返回第一个活敌（非"被阻挡的敌人"），P3 改造时须重写此逻辑。
- `make_arts_master` 无路径（`path=[]`），所以不会尝试前进到目标（`advance` 永远不到达），测试中 Arts Master 只能被打死——符合当前 1v1 demo 语义。
