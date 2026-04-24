"""Folinic (稀音) — 5★ Supporter (Summoner).

S1 "Camouflage": sp_cost=72, initial_sp=0, toggle (permanent), AUTO_TIME, MANUAL.
  ATK+30%; 3600s sentinel duration — toggle-off not modeled.

S2 "Panoramic Camera Overload": sp_cost=30, initial_sp=9, duration=17s, AUTO_TIME, MANUAL.
  ATK+80% + DEF+80% + RES+15; stun on target not modeled — stub.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.folivo import make_folivo as _base_stats

SUP_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 3) for dy in range(-1, 2)
))

_S1_TAG = "folivo_s1_camouflage"
_S1_ATK_RATIO = 0.30
_S1_BUFF_TAG = "folivo_s1_atk"
_S1_DURATION = 3600.0  # toggle sentinel; deactivation not modeled

_S2_TAG = "folivo_s2_panoramic_overload"
_S2_DURATION = 17.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_folivo(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Folinic"
    op.archetype = RoleArchetype.SUP_SUMMONER
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.range_shape = SUP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Camouflage", slot="S1", sp_cost=72, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Panoramic Camera Overload", slot="S2", sp_cost=30, initial_sp=9,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
