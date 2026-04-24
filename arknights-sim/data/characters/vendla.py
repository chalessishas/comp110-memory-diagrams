"""Vendla (刺玫) — 5★ Medic (Incantation) (char_4128_vendla).

S1: sp_cost=10, initial_sp=5, duration=5s, AUTO_TIME, AUTO — stub.

S2 "战术咏唱·γ型" (Tactical Chant γ): sp_cost=30, initial_sp=15, duration=30s, AUTO_TIME, MANUAL.
  ASPD+90.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.vendla import make_vendla as _base_stats

MEDIC_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))

_S1_TAG = "vendla_s1"
_S1_DURATION = 5.0

_S2_TAG = "vendla_s2_tactical_chant"
_S2_ASPD_VALUE = 90.0
_S2_ASPD_BUFF_TAG = "vendla_s2_aspd"
_S2_DURATION = 30.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
                              value=_S2_ASPD_VALUE, source_tag=_S2_ASPD_BUFF_TAG))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_ASPD_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_vendla(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Vendla"
    op.archetype = RoleArchetype.MEDIC_INCANTATION
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.range_shape = MEDIC_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Vendla S1", slot="S1", sp_cost=10, initial_sp=5,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Tactical Chant", slot="S2", sp_cost=30, initial_sp=15,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
