"""Elysium (爱丽丝) — 5★ Vanguard (Agent).

Both skills involve DP recovery and debuffs — behavior not modeled.

S1: sp_cost=29, initial_sp=12, duration=8s, AUTO_TIME, MANUAL (stub).
S2: sp_cost=34, initial_sp=10, duration=15s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.elysm import make_elysm as _base_stats

VAN_RANGE = RangeShape(tiles=((0, 0), (1, 0)))
_S1_TAG = "elysm_s1"; _S1_DURATION = 8.0
_S2_TAG = "elysm_s2"; _S2_DURATION = 15.0


def make_elysm(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Elysm"
    op.archetype = RoleArchetype.VAN_AGENT
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = VAN_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Elysm S1", slot="S1", sp_cost=29, initial_sp=12,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Elysm S2", slot="S2", sp_cost=34, initial_sp=10,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
