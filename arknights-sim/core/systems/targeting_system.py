"""Targeting — 为每个活着的 unit 确定本 tick 的主目标.

Terra Wiki 优先级栈（从高到低）:
  1. Blocked unit           —— 被阻挡的敌人优先
  2. Special Priority       —— 低抗性 / 高威胁 / 职业分支特定
  3. Highest aggression     —— a = 1000*(t+s) 近似：部署时间大的 + 路径进度深的
  4. Closest to destination —— 我们用 _path_progress 最大
  5. Highest negative aggression —— 隐身等特殊负优先

本实现覆盖 1 + 3 + 4（最常用的三条），Special 预留 hook.
"""
from __future__ import annotations
from typing import List, Optional
from ..types import Faction, StatusKind
from ..state.unit_state import UnitState


def _enemy_in_range(op: UnitState, enemy: UnitState) -> bool:
    """Check if enemy is within op's range_shape (relative to op.position)."""
    if op.position is None or enemy.position is None:
        return False
    ox, oy = op.position
    ex, ey = enemy.position

    # 整数相对坐标：敌人所在格 - 干员所在格
    dx_int = round(ex) - round(ox)
    dy_int = round(ey) - round(oy)

    # 若启用了 extended range (S2 等)，合并两套
    shape = op.range_shape
    tiles = set(shape.tiles)
    if shape.extended_tiles:
        tiles |= set(shape.extended_tiles)

    return (dx_int, dy_int) in tiles


def _targeting_for_operator(world, op: UnitState) -> Optional[UnitState]:
    from ..types import AttackType
    if not op.can_act():
        return None
    if not op.deployed or op.position is None:
        return None

    # Healer: target most-injured ally (lowest hp/max_hp ratio)
    if op.attack_type == AttackType.HEAL:
        candidates = [u for u in world.allies() if u.alive and u.hp < u.max_hp]
        if not candidates:
            return None
        return min(candidates, key=lambda u: u.hp / u.max_hp)

    # Collect in-range live enemies
    candidates: List[UnitState] = [
        e for e in world.enemies()
        if _enemy_in_range(op, e) and not e.has_status(StatusKind.CAMOUFLAGE)
    ]
    if not candidates:
        return None

    # Rule 1: blocked enemies first
    blocked = [e for e in candidates if op.unit_id in e.blocked_by_unit_ids]
    if blocked:
        return max(blocked, key=lambda e: e.path_progress)

    # Rule 3/4: highest aggression ≈ highest path_progress
    return max(candidates, key=lambda e: e.path_progress)


def _targeting_for_enemy(world, enemy: UnitState) -> Optional[UnitState]:
    """敌人攻击阻挡它的最早部署的干员 (Terra Wiki)."""
    if not enemy.can_act():
        return None
    if not enemy.blocked_by_unit_ids:
        return None
    # 找第一个存活的阻挡者
    for uid in enemy.blocked_by_unit_ids:
        u = world.unit_by_id(uid)
        if u and u.alive:
            return u
    return None


def targeting_system(world, dt: float) -> None:
    """Writes to unit.__current_target__ (a dynamic attribute, cleared each tick)."""
    # 更新 blocked_by
    _update_block_assignments(world)

    for u in world.units:
        if not u.alive:
            setattr(u, "__target__", None)
            continue
        if u.faction == Faction.ALLY:
            setattr(u, "__target__", _targeting_for_operator(world, u))
        else:
            setattr(u, "__target__", _targeting_for_enemy(world, u))


def _update_block_assignments(world) -> None:
    """Each melee ally blocks up to `block` enemies currently on/near its tile."""
    from ..types import Mobility
    # 清空所有 enemy.blocked_by_unit_ids
    for e in world.enemies():
        e.blocked_by_unit_ids = []

    for op in world.allies():
        if not op.deployed or op.block == 0 or op.position is None:
            continue
        ox, oy = op.position
        # Greedy: pick the `block` enemies closest to op.position
        nearby = [
            e for e in world.enemies()
            if e.position is not None
            and e.mobility != Mobility.AIRBORNE           # aerial bypasses block
            and abs(round(e.position[0]) - round(ox)) <= 0
            and abs(round(e.position[1]) - round(oy)) <= 0
            and len(e.blocked_by_unit_ids) == 0  # not already blocked
        ]
        # Sort by path_progress descending (block the furthest-along first)
        nearby.sort(key=lambda e: -e.path_progress)
        for e in nearby[: op.block]:
            e.blocked_by_unit_ids.append(op.unit_id)
