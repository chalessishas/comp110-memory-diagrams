"""Nowell (诺威尔) — 4★ Medic (char_4173).

S1 "步履不停" (Keep Moving): sp_cost=30, initial_sp=20, duration=30s, AUTO_TIME, MANUAL.
  ATK+40%, ASPD+40.

S2: sp_cost=30, initial_sp=15, duration=20s — stub.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.nowell import make_nowell as _base_stats

MEDIC_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))

_S1_TAG = "nowell_s1_keep_moving"
_S1_ATK_RATIO = 0.40
_S1_ASPD_VALUE = 40.0
_S1_ATK_BUFF_TAG = "nowell_s1_atk"
_S1_ASPD_BUFF_TAG = "nowell_s1_aspd"
_S1_DURATION = 30.0

_S2_TAG = "nowell_s2"
_S2_DURATION = 20.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_ATK_BUFF_TAG))
    carrier.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
                              value=_S1_ASPD_VALUE, source_tag=_S1_ASPD_BUFF_TAG))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S1_ATK_BUFF_TAG, _S1_ASPD_BUFF_TAG)]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_nowell(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Nowell"
    op.archetype = RoleArchetype.MEDIC_ST
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.range_shape = MEDIC_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Keep Moving", slot="S1", sp_cost=30, initial_sp=20,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Nowell S2", slot="S2", sp_cost=30, initial_sp=15,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
