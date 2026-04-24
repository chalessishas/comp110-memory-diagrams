"""Ceobe (刻俄柏) — 6★ Caster (Core).

S1 "Really Cold Axe": sp_cost=7, initial_sp=0, instant (2-charge burst, stub).
S2 "Really Hot Knives": sp_cost=44, initial_sp=16, 36s (interval ×0.4 + DEF-target, stub).
S3 "Really Heavy Spear": sp_cost=80, initial_sp=47, 57s. ATK+160%.
  Physical dmg-type swap during skill not modeled (attack_type is static).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.cerber import make_cerber as _base_stats

CASTER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
))

_S1_TAG = "cerber_s1_cold_axe"
_S2_TAG = "cerber_s2_hot_knives"
_S2_DURATION = 36.0
_S3_TAG = "cerber_s3_heavy_spear"
_S3_ATK_RATIO = 1.60
_S3_BUFF_TAG = "cerber_s3_atk"
_S3_DURATION = 57.0


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))
    world.log(f"Ceobe S3 — ATK+{_S3_ATK_RATIO:.0%}/{_S3_DURATION}s (phys swap not modeled)")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_cerber(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Ceobe"
    op.archetype = RoleArchetype.CASTER_CORE
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CASTER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Really Cold Axe", slot="S1", sp_cost=7, initial_sp=0,
            duration=0.0, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Really Hot Knives", slot="S2", sp_cost=44, initial_sp=16,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Really Heavy Spear", slot="S3", sp_cost=80, initial_sp=47,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
