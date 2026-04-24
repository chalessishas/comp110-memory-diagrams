"""Greyy the Lightchaser (承曦格雷伊) — 5★ Sniper (Deadeye).

S1: sp_cost=4, initial_sp=0, instant, AUTO_ATTACK, AUTO (stub).
S2 "Swift Strike": sp_cost=39, initial_sp=10, duration=35s, AUTO_TIME, MANUAL.
  ATK+34%, ASPD+35. Slow on first attack not modeled.
S3: sp_cost=60, initial_sp=30, duration=20s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.greyy2 import make_greyy2 as _base_stats

SNIPER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 4) for dy in range(-2, 3)
))

_S1_TAG = "greyy2_s1"
_S1_DURATION = 0.0

_S2_TAG = "greyy2_s2_swift_strike"
_S2_ATK_RATIO = 0.34
_S2_ASPD_FLAT = 35.0
_S2_ATK_BUFF_TAG = "greyy2_s2_atk"
_S2_ASPD_BUFF_TAG = "greyy2_s2_aspd"
_S2_DURATION = 35.0

_S3_TAG = "greyy2_s3"
_S3_DURATION = 20.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=_S2_ASPD_FLAT, source_tag=_S2_ASPD_BUFF_TAG,
    ))
    world.log(f"Greyy the Lightchaser S2 — ATK+{_S2_ATK_RATIO:.0%} ASPD+{_S2_ASPD_FLAT:.0f}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S2_ATK_BUFF_TAG, _S2_ASPD_BUFF_TAG)]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_greyy2(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Greyy the Lightchaser"
    op.archetype = RoleArchetype.SNIPER_DEADEYE
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNIPER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Greyy the Lightchaser S1", slot="S1", sp_cost=4, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Swift Strike", slot="S2", sp_cost=39, initial_sp=10,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Greyy the Lightchaser S3", slot="S3", sp_cost=60, initial_sp=30,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
