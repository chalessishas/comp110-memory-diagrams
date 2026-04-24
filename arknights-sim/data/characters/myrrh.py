"""Myrrh (没药) — 4★ Medic (ST) (char_187_ccheal).

S1: sp_cost=8, initial_sp=0, instant, AUTO_TIME, AUTO (stub).
S2 "Medical Field" (skchr_myrrh_2): sp_cost=50, initial_sp=20, duration=25s, AUTO_TIME, MANUAL.
  ATK+65%.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.myrrh import make_myrrh as _base_stats

MEDIC_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))

_S1_TAG = "myrrh_s1"
_S1_DURATION = 0.0

_S2_TAG = "myrrh_s2_medical_field"
_S2_ATK_RATIO = 0.65
_S2_ATK_BUFF_TAG = "myrrh_s2_atk"
_S2_DURATION = 25.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_ATK_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_myrrh(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Myrrh"
    op.archetype = RoleArchetype.MEDIC_ST
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.range_shape = MEDIC_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Myrrh S1", slot="S1", sp_cost=8, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Medical Field", slot="S2", sp_cost=50, initial_sp=20,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
