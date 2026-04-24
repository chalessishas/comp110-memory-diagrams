"""Hazel (褐果) — 4★ Medic (Wandering).

S1 "Tiny Steps, Giant Strides": sp_cost=14, initial_sp=6, duration=6s, AUTO_TIME, MANUAL
  (instant heal + elemental damage recovery ×250%, 2 charges — stub).
S2 "Earthburst": sp_cost=74, initial_sp=30, duration=35s, AUTO_TIME, MANUAL.
  ASPD+100. Elemental recovery and sustained-target bonus not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.chnut import make_chnut as _base_stats

MEDIC_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 3) for dy in range(-1, 2)
))

_S1_TAG = "chnut_s1_tiny_steps"
_S1_DURATION = 6.0

_S2_TAG = "chnut_s2_earthburst"
_S2_ASPD_BONUS = 100.0
_S2_BUFF_TAG = "chnut_s2_aspd"
_S2_DURATION = 35.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
                              value=_S2_ASPD_BONUS, source_tag=_S2_BUFF_TAG))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_chnut(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Hazel"
    op.archetype = RoleArchetype.MEDIC_WANDERING
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.range_shape = MEDIC_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Tiny Steps, Giant Strides", slot="S1", sp_cost=14, initial_sp=6,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Earthburst", slot="S2", sp_cost=74, initial_sp=30,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
