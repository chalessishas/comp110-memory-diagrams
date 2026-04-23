"""Blacknight (夜半) — 5★ Pioneer Vanguard.

S1 "Drowsy": sp_cost=28, initial_sp=14, duration=10s, AUTO_TIME, MANUAL
  (+11 DP; Slumberfoot sleeps + regen HP; on-damage-wake ATK+40% ASPD+40; summon + conditional — stub).
S2 "Peaceful Slumber": sp_cost=17, initial_sp=10, duration=5s, AUTO_TIME, MANUAL
  (+4 DP; Sleep enemies near Tactical Point 5s; Slumberfoot AOE Arts vs sleeping; 2 charges — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.blkngt import make_blkngt as _base_stats

PIONEER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "blkngt_s1_drowsy"
_S1_DURATION = 10.0

_S2_TAG = "blkngt_s2_peaceful_slumber"
_S2_DURATION = 5.0


def make_blkngt(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Blacknight"
    op.archetype = RoleArchetype.VAN_PIONEER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = PIONEER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Drowsy", slot="S1", sp_cost=28, initial_sp=14,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Peaceful Slumber", slot="S2", sp_cost=17, initial_sp=10,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
