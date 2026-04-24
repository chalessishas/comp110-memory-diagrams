"""Lappland (拉普兰德) — 5★ Guard (Lord) (char_140_whitew).

S1: sp_cost=5, initial_sp=0, instant, AUTO_ATTACK, AUTO (stub).
S2 "狼魂" (Wolf Spirit): sp_cost=17, initial_sp=0, duration=20s, AUTO_ATTACK, AUTO.
  ATK+120%.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.whitew import make_whitew as _base_stats

OP_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "whitew_s1"
_S1_DURATION = 0.0

_S2_TAG = "whitew_s2_wolf_spirit"
_S2_ATK_RATIO = 1.20
_S2_ATK_BUFF_TAG = "whitew_s2_atk"
_S2_DURATION = 20.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_ATK_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_whitew(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Lappland"
    op.archetype = RoleArchetype.GUARD_LORD
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = OP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Lappland S1", slot="S1", sp_cost=5, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Wolf Spirit", slot="S2", sp_cost=17, initial_sp=0,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
