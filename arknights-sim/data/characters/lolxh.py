"""Luo Xiaohei (罗小黑) — 5★ Guard (Fighter).

S1: sp_cost=3, initial_sp=0, instant, AUTO_ATTACK, AUTO (stub).
S2 "Broken Blade": ATK+40%/20s, sp_cost=40, initial_sp=10, AUTO_TIME, MANUAL.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import AttackType, BuffAxis, BuffStack, Profession, RoleArchetype, SkillTrigger, SPGainMode
from core.systems.skill_system import register_skill
from data.characters.generated.lolxh import make_lolxh as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))
_S1_TAG = "lolxh_s1"; _S1_DURATION = 0.0
_S2_TAG = "lolxh_s2_broken_blade"; _S2_DURATION = 20.0
_S2_ATK_RATIO = 0.40
_S2_BUFF_TAG = "lolxh_s2_atk"


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_lolxh(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Lolxh"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Lolxh S1", slot="S1", sp_cost=3, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Broken Blade", slot="S2", sp_cost=40, initial_sp=10,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
