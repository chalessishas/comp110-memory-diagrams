"""Haak (阿) — 6★ Specialist (Executor) (char_225_haak).

S1 "Quick Shot": sp_cost=30, initial_sp=20, duration=30s, AUTO_TIME, MANUAL.
  ASPD+100.

S2: sp_cost=40, initial_sp=20, duration=25s — stub.
S3: sp_cost=60, initial_sp=30, duration=30s — stub.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.haak import make_haak as _base_stats

SPEC_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "haak_s1_quick_shot"
_S1_ASPD_VALUE = 100.0
_S1_ASPD_BUFF_TAG = "haak_s1_aspd"
_S1_DURATION = 30.0

_S2_TAG = "haak_s2"
_S2_DURATION = 25.0

_S3_TAG = "haak_s3"
_S3_DURATION = 30.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
                              value=_S1_ASPD_VALUE, source_tag=_S1_ASPD_BUFF_TAG))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_ASPD_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_haak(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Haak"
    op.archetype = RoleArchetype.SPEC_EXECUTOR
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SPEC_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Quick Shot", slot="S1", sp_cost=30, initial_sp=20,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Haak S2", slot="S2", sp_cost=40, initial_sp=20,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Haak S3", slot="S3", sp_cost=60, initial_sp=30,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
