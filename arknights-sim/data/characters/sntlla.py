"""Santalla (寒檀) — 5★ Caster (Core).

S1 "Quick Strike γ" (skcom_quickattack[3]): sp_cost=35, initial_sp=15, duration=35s, AUTO_TIME, MANUAL.
  ATK+45%, ASPD+45.

S2: sp_cost=35, initial_sp=18, duration=15s — stub.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.sntlla import make_sntlla as _base_stats

CAST_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))

_S1_TAG = "sntlla_s1_quick_strike"
_S1_ATK_RATIO = 0.45
_S1_ATK_BUFF_TAG = "sntlla_s1_atk"
_S1_ASPD_VALUE = 45.0
_S1_ASPD_BUFF_TAG = "sntlla_s1_aspd"
_S1_DURATION = 35.0

_S2_TAG = "sntlla_s2"
_S2_DURATION = 15.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_ATK_BUFF_TAG))
    carrier.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
                              value=_S1_ASPD_VALUE, source_tag=_S1_ASPD_BUFF_TAG))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S1_ATK_BUFF_TAG, _S1_ASPD_BUFF_TAG)]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_sntlla(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Santalla"
    op.archetype = RoleArchetype.CASTER_CORE
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CAST_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Quick Strike γ", slot="S1", sp_cost=35, initial_sp=15,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Sntlla S2", slot="S2", sp_cost=35, initial_sp=18,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
