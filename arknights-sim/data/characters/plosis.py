"""Plosis (Ptilopsis 白面鸮) — 5★ Medic (ST) (char_171_bldsk).

S1 "治疗强化·γ型" (Healing Enhancement γ): sp_cost=30, initial_sp=20, duration=30s, AUTO_TIME, MANUAL.
  ATK+90%.

S2: sp_cost=100, initial_sp=85, duration=40s — stub.
Note: extreme initial_sp on S2 reflects her SP-regen talent at E2.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.plosis import make_plosis as _base_stats

MEDIC_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))

_S1_TAG = "plosis_s1_healing_enhance"
_S1_ATK_RATIO = 0.90
_S1_ATK_BUFF_TAG = "plosis_s1_atk"
_S1_DURATION = 30.0

_S2_TAG = "plosis_s2"
_S2_DURATION = 40.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_ATK_BUFF_TAG))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_ATK_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_plosis(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Ptilopsis"
    op.archetype = RoleArchetype.MEDIC_ST
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.range_shape = MEDIC_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Healing Enhancement γ", slot="S1", sp_cost=30, initial_sp=20,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Ptilopsis S2", slot="S2", sp_cost=100, initial_sp=85,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
