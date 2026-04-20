"""Shamare (沙马尔) — 5★ Supporter (Hexer archetype).

SUP_HEXER trait: Attacks reduce enemy ATK and DEF.

Talent "Rancor": Each normal attack applies ATK_DOWN (−25%) and DEF_DOWN (−25%)
  to the target for 10s. Refresh semantics on repeat hits.

S2 "Puppetmaster": Instant AoE — applies FRAGILE (+65% damage taken) to all
  enemies in attack range for 20s.
  sp_cost=25, initial_sp=10, AUTO_TIME, AUTO trigger, requires_target=False.

Base stats (E2 max, trust 100, char_1014_nearl2 approximate — no generated file).
  HP=1640, ATK=396, DEF=117, RES=0, atk_interval=2.05s, cost=12, block=1.
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape,
    TalentComponent, StatusEffect,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent


SUP_HEXER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 4) for dy in range(-1, 2)
))

# --- Talent: Rancor ---
_TALENT_TAG = "shamare_rancor"
_RANCOR_ATK_RATIO = 0.25       # −25% ATK reduction
_RANCOR_DEF_RATIO = 0.25       # −25% DEF reduction
_RANCOR_DURATION = 10.0
_RANCOR_ATK_TAG = "shamare_rancor_atk"
_RANCOR_DEF_TAG = "shamare_rancor_def"

# --- S2: Puppetmaster ---
_S2_TAG = "shamare_s2_puppetmaster"
_S2_FRAGILE_AMOUNT = 0.65      # target takes +65% damage
_S2_FRAGILE_DURATION = 20.0
_S2_FRAGILE_TAG = "shamare_s2_fragile"


def _rancor_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    elapsed = world.global_state.elapsed
    expires = elapsed + _RANCOR_DURATION

    # Refresh: remove stale then re-apply both debuffs
    target.statuses = [s for s in target.statuses
                       if s.source_tag not in (_RANCOR_ATK_TAG, _RANCOR_DEF_TAG)]
    target.buffs = [b for b in target.buffs
                    if b.source_tag not in (_RANCOR_ATK_TAG, _RANCOR_DEF_TAG)]

    target.statuses.append(StatusEffect(
        kind=StatusKind.ATK_DOWN,
        source_tag=_RANCOR_ATK_TAG,
        expires_at=expires,
        params={"amount": _RANCOR_ATK_RATIO},
    ))
    target.buffs.append(Buff(
        axis=BuffAxis.ATK,
        stack=BuffStack.RATIO,
        value=-_RANCOR_ATK_RATIO,
        source_tag=_RANCOR_ATK_TAG,
        expires_at=expires,
    ))
    target.statuses.append(StatusEffect(
        kind=StatusKind.DEF_DOWN,
        source_tag=_RANCOR_DEF_TAG,
        expires_at=expires,
        params={"amount": _RANCOR_DEF_RATIO},
    ))
    target.buffs.append(Buff(
        axis=BuffAxis.DEF,
        stack=BuffStack.RATIO,
        value=-_RANCOR_DEF_RATIO,
        source_tag=_RANCOR_DEF_TAG,
        expires_at=expires,
    ))
    world.log(
        f"Shamare Rancor → {target.name}  "
        f"ATK_DOWN/DEF_DOWN −{_RANCOR_ATK_RATIO:.0%}  ({_RANCOR_DURATION}s)"
    )


register_talent(_TALENT_TAG, on_attack_hit=_rancor_on_attack_hit)


def _enemy_in_range(op: UnitState, enemy: UnitState) -> bool:
    if op.position is None or enemy.position is None:
        return False
    ox, oy = op.position
    ex, ey = enemy.position
    dx = round(ex) - round(ox)
    dy = round(ey) - round(oy)
    return (dx, dy) in set(op.range_shape.tiles)


def _s2_on_start(world, carrier: UnitState) -> None:
    now = world.global_state.elapsed
    count = 0
    for enemy in world.enemies():
        if not enemy.deployed:
            continue
        if not _enemy_in_range(carrier, enemy):
            continue
        enemy.statuses = [s for s in enemy.statuses if s.source_tag != _S2_FRAGILE_TAG]
        enemy.statuses.append(StatusEffect(
            kind=StatusKind.FRAGILE,
            source_tag=_S2_FRAGILE_TAG,
            expires_at=now + _S2_FRAGILE_DURATION,
            params={"amount": _S2_FRAGILE_AMOUNT},
        ))
        count += 1
    world.log(f"Shamare S2 Puppetmaster — FRAGILE +{_S2_FRAGILE_AMOUNT:.0%} × {count} enemy")


register_skill(_S2_TAG, on_start=_s2_on_start)


def make_shamare(slot: str = "S2") -> UnitState:
    """Shamare E2 max. SUP_HEXER: Rancor ATK/DEF -25% on hit; S2: AoE FRAGILE +65%."""
    op = UnitState(
        name="Shamare",
        faction=Faction.ALLY,
        max_hp=1640,
        hp=1640,
        atk=396,
        defence=117,
        res=0.0,
        atk_interval=2.05,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=12,
        redeploy_cd=70.0,
        deployed=False,
        range_shape=SUP_HEXER_RANGE,
    )
    op.archetype = RoleArchetype.SUP_HEXER
    op.talents = [TalentComponent(name="Rancor", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Puppetmaster",
            slot="S2",
            sp_cost=25,
            initial_sp=10,
            duration=0.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
