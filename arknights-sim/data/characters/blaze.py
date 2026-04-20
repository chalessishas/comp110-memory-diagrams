"""Blaze (暴行) — 6* Guard (Centurion archetype).

Centurion trait: Attacks all currently-blocked enemies simultaneously.
  Implemented via targeting_system GUARD_CENTURION __targets__ branch.

Talent "Passion" (E2): When this unit is blocking ≥ 1 enemy, ATK +15%.
  Short-lived buff refreshed every tick (same pattern as Mountain/Bagpipe).

S2 "Carnage": Instant (duration=0). Deals _S2_ATK_MULTIPLIER × ATK physical
  damage to ALL enemies in range simultaneously.
  sp_cost=25, initial_sp=10, AUTO_TIME, MANUAL trigger.

S3 "Blazing Sun": ATK +220%, 40s duration.
  sp_cost=35, initial_sp=15, AUTO_TIME, requires_target=True.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession, RoleArchetype,
    SPGainMode, SkillTrigger,
)
from math import floor
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.savage import make_savage as _base_stats


CENTURION_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_PASSION_TAG = "blaze_passion"
_PASSION_ATK_RATIO = 0.15
_PASSION_BUFF_TAG = "blaze_passion_atk"
_PASSION_REFRESH_DT = 0.2   # short-lived; refreshed every 0.1s tick when blocking

_S2_TAG = "blaze_s2_carnage"
_S2_ATK_MULTIPLIER = 1.90   # 100% base + 90% bonus = 190% of ATK

_S3_TAG = "blaze_s3_blazing_sun"
_S3_ATK_RATIO = 2.20
_S3_BUFF_TAG = "blaze_s3_atk"


def _passion_on_tick(world, carrier, dt: float) -> None:
    now = world.global_state.elapsed
    is_blocking = any(carrier.unit_id in e.blocked_by_unit_ids for e in world.enemies())
    if is_blocking:
        for b in carrier.buffs:
            if b.source_tag == _PASSION_BUFF_TAG:
                b.expires_at = now + _PASSION_REFRESH_DT
                break
        else:
            carrier.buffs.append(Buff(
                axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                value=_PASSION_ATK_RATIO, source_tag=_PASSION_BUFF_TAG,
                expires_at=now + _PASSION_REFRESH_DT,
            ))


register_talent(_PASSION_TAG, on_tick=_passion_on_tick)


# --- S2: Carnage (instant AOE burst) ---
def _s2_on_start(world, carrier: UnitState) -> None:
    if carrier.position is None:
        return
    ox, oy = carrier.position
    tiles = set(carrier.range_shape.tiles)
    burst_atk = int(floor(carrier.effective_atk * _S2_ATK_MULTIPLIER))
    for enemy in list(world.enemies()):
        if enemy.position is None:
            continue
        dx = round(enemy.position[0]) - round(ox)
        dy = round(enemy.position[1]) - round(oy)
        if (dx, dy) not in tiles:
            continue
        dealt = enemy.take_physical(burst_atk)
        world.global_state.total_damage_dealt += dealt
        world.log(f"Blaze S2 → {enemy.name}  dmg={dealt}  ({enemy.hp}/{enemy.max_hp})")


register_skill(_S2_TAG, on_start=_s2_on_start)


# --- S3: Blazing Sun ---
def _s3_on_start(world, unit) -> None:
    unit.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))


def _s3_on_end(world, unit) -> None:
    unit.buffs = [b for b in unit.buffs if b.source_tag != _S3_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_blaze(slot: str = "S3") -> UnitState:
    """Blaze E2 max. Centurion: hits all blocked. Talent ATK+15% when blocking. S2: instant AOE. S3: ATK+220%/40s."""
    op = _base_stats()
    op.name = "Blaze"
    op.archetype = RoleArchetype.GUARD_CENTURION
    op.profession = Profession.GUARD
    op.range_shape = CENTURION_RANGE
    op.block = 3
    op.cost = 22
    op.talents = [TalentComponent(name="Passion", behavior_tag=_PASSION_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Carnage",
            slot="S2",
            sp_cost=25,
            initial_sp=10,
            duration=0.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Blazing Sun",
            slot="S3",
            sp_cost=35,
            initial_sp=15,
            duration=40.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
    return op
