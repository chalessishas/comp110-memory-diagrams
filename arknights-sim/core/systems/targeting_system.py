"""Targeting — 为每个活着的 unit 确定本 tick 的主目标.

Terra Wiki 优先级栈（从高到低）:
  1. Blocked unit           —— 被阻挡的敌人优先
  2. Special Priority       —— 低抗性 / 高威胁 / 职业分支特定
  3. Highest aggression     —— a = 1000*(t+s) 近似：部署时间大的 + 路径进度深的
  4. Closest to destination —— min path_distance_remaining (correct for multi-route stages)
  5. Highest negative aggression —— 隐身等特殊负优先

本实现覆盖 1 + 3 + 4（最常用的三条），Special 预留 hook.

Aerial targeting rule:
  attack_range_melee=True operators CANNOT target Mobility.AIRBORNE enemies.
  SNIPER_ANTI_AIR operators prioritize AIRBORNE enemies over ground enemies.
"""
from __future__ import annotations
from typing import List, Optional
from ..types import AttackType, Faction, Mobility, RoleArchetype, StatusKind
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
    # Musha Guards with heal_block_threshold > 0 are excluded when above their threshold
    if op.attack_type == AttackType.HEAL:
        candidates = [
            u for u in world.allies()
            if u.alive and u.hp < u.max_hp
            and (u.heal_block_threshold == 0.0
                 or u.hp / u.max_hp < u.heal_block_threshold)
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda u: u.hp / u.max_hp)

    # Collect in-range live enemies
    all_in_range: List[UnitState] = [
        e for e in world.enemies()
        if _enemy_in_range(op, e) and not e.has_status(StatusKind.CAMOUFLAGE)
    ]
    if not all_in_range:
        return None

    # Aerial targeting restriction: melee operators cannot target airborne enemies
    if op.attack_range_melee:
        candidates = [e for e in all_in_range if e.mobility != Mobility.AIRBORNE]
    else:
        candidates = all_in_range

    if not candidates:
        return None

    def _dist_remaining(e: UnitState) -> float:
        path_len = len(e.path) - 1 if e.path else 0
        return max(0.0, path_len - e.path_progress)

    # Rule 1: blocked enemies first — min path_distance_remaining
    blocked = [e for e in candidates if op.unit_id in e.blocked_by_unit_ids]
    if blocked:
        return min(blocked, key=_dist_remaining)

    # Archetype-specific priority overrides (applied to unblocked candidates)
    if op.archetype == RoleArchetype.SNIPER_DEADEYE:
        # Deadeye Sniper trait: target enemy with lowest DEF
        return min(candidates, key=lambda e: (e.defence, _dist_remaining(e)))
    if op.archetype == RoleArchetype.SNIPER_SIEGE:
        # Besieger Sniper trait: target enemy with highest weight
        return max(candidates, key=lambda e: (e.weight, -_dist_remaining(e)))
    if op.archetype == RoleArchetype.SNIPER_ANTI_AIR:
        # Anti-Air Sniper trait: prefer airborne enemies, then closest to exit
        airborne = [e for e in candidates if e.mobility == Mobility.AIRBORNE]
        pool = airborne if airborne else candidates
        return min(pool, key=_dist_remaining)

    # Rule 3/4: closest to destination — min path_distance_remaining
    return min(candidates, key=_dist_remaining)


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


def _is_fortress_blocking(world, op: UnitState) -> bool:
    """True when this Fortress Defender is currently blocking at least one enemy."""
    return any(op.unit_id in e.blocked_by_unit_ids for e in world.enemies())


def targeting_system(world, dt: float) -> None:
    """Writes to unit.__target__ and (for Fortress) __targets__ each tick."""
    _update_block_assignments(world)

    for u in world.units:
        if not u.alive:
            setattr(u, "__target__", None)
            setattr(u, "__targets__", [])
            continue
        if u.faction == Faction.ALLY:
            if u.archetype == RoleArchetype.DEF_FORTRESS:
                # Fortress Defender: ranged-AoE when not blocking, melee single when blocking
                if _is_fortress_blocking(world, u):
                    # Melee mode: temporarily use melee range for target selection
                    melee_range = getattr(u, "_melee_range", u.range_shape)
                    saved_range = u.range_shape
                    u.range_shape = melee_range
                    setattr(u, "__target__", _targeting_for_operator(world, u))
                    u.range_shape = saved_range
                    setattr(u, "__targets__", [])
                else:
                    # Ranged mode: range_shape is already the ranged shape
                    # Attack ALL in-range enemies simultaneously
                    candidates = [
                        e for e in world.enemies()
                        if u.deployed and u.position is not None
                        and _enemy_in_range(u, e)
                        and not e.has_status(StatusKind.CAMOUFLAGE)
                        and e.alive
                    ]
                    setattr(u, "__target__", None)
                    setattr(u, "__targets__", candidates)
            elif u.archetype == RoleArchetype.SUP_BARD:
                # Bard Supporter trait: never attacks; SP aura handled by on_tick talent
                setattr(u, "__target__", None)
                setattr(u, "__targets__", [])
            elif u.archetype == RoleArchetype.GUARD_CENTURION:
                # Centurion Guard trait: attack all currently-blocked enemies simultaneously
                blocked = [
                    e for e in world.enemies()
                    if u.unit_id in e.blocked_by_unit_ids and e.alive
                ]
                if blocked:
                    setattr(u, "__target__", None)
                    setattr(u, "__targets__", blocked)
                else:
                    # No blocked enemies — fall back to normal single-target
                    setattr(u, "__target__", _targeting_for_operator(world, u))
                    setattr(u, "__targets__", [])
            elif u.attack_type == AttackType.HEAL and u.heal_targets > 1:
                # Multi-target medic: heal top-N most-injured allies simultaneously
                # Exclude Musha Guards above their heal-block threshold
                injured = sorted(
                    [
                        a for a in world.allies()
                        if a.alive and a.hp < a.max_hp
                        and (a.heal_block_threshold == 0.0
                             or a.hp / a.max_hp < a.heal_block_threshold)
                    ],
                    key=lambda a: a.hp / a.max_hp,
                )
                setattr(u, "__target__", None)
                setattr(u, "__targets__", injured[: u.heal_targets])
            elif getattr(u, "_attack_all_in_range", False):
                # Generic AOE attack override (e.g. Thorns S3) — hit every enemy in range
                candidates = [
                    e for e in world.enemies()
                    if u.deployed and u.position is not None
                    and _enemy_in_range(u, e)
                    and not e.has_status(StatusKind.CAMOUFLAGE)
                    and e.alive
                ]
                setattr(u, "__target__", None)
                setattr(u, "__targets__", candidates)
            else:
                setattr(u, "__target__", _targeting_for_operator(world, u))
                setattr(u, "__targets__", [])
        else:
            setattr(u, "__target__", _targeting_for_enemy(world, u))
            setattr(u, "__targets__", [])


def _update_block_assignments(world) -> None:
    """Each melee ally blocks up to `block` enemies currently on/near its tile."""
    # 清空所有 enemy.blocked_by_unit_ids
    for e in world.enemies():
        e.blocked_by_unit_ids = []

    # CAMOUFLAGE operators are preferred last for block assignment —
    # enemies "don't see" them when a visible operator is available.
    allies_sorted = sorted(
        world.allies(),
        key=lambda u: 1 if u.has_status(StatusKind.CAMOUFLAGE) else 0,
    )
    for op in allies_sorted:
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
        # Block the enemy closest to exit first (min remaining distance)
        nearby.sort(key=lambda e: max(0.0, (len(e.path) - 1 if e.path else 0) - e.path_progress))
        for e in nearby[: op.block]:
            e.blocked_by_unit_ids.append(op.unit_id)
