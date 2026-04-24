"""Laios (莱欧斯) — 5★ Guard (Dreadnought).

S1 "Devouring Slash": sp_cost=0, initial_sp=0, duration=9999s, ON_DEPLOY, AUTO (passive stub).
  Always-active passive; effect not modeled.
S2 "Intimidation": sp_cost=22, initial_sp=10, duration=10s, AUTO_TIME, MANUAL (stub).
  ATK buff + taunt effect not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.laios import make_laios as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "laios_s1"
_S1_DURATION = 9999.0

_S2_TAG = "laios_s2"
_S2_DURATION = 10.0


def make_laios(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Laios"
    op.archetype = RoleArchetype.GUARD_DREADNOUGHT
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Devouring Slash", slot="S1", sp_cost=0, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.ON_DEPLOY,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Intimidation", slot="S2", sp_cost=22, initial_sp=10,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
