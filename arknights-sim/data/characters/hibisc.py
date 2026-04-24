"""Hibiscus (芙蓉) — 4★ Medic (char_120).

S1 "治疗强化·α型" (Healing Enhancement α): sp_cost=30, initial_sp=0, duration=20s, AUTO_TIME, MANUAL.
  ATK+50% (heal amount boost).

Hibiscus has only one skill slot (no S2).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.hibisc import make_hibisc as _base_stats

MEDIC_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))

_S1_TAG = "hibisc_s1_heal_up_alpha"
_S1_ATK_RATIO = 0.50
_S1_ATK_BUFF_TAG = "hibisc_s1_atk"
_S1_DURATION = 20.0

_S2_TAG = "hibisc_s2"  # hibisc has no S2; kept for compat


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_ATK_BUFF_TAG))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_ATK_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_hibisc(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Hibiscus"
    op.archetype = RoleArchetype.MEDIC_ST
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.range_shape = MEDIC_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Healing Enhancement α", slot="S1", sp_cost=30, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
