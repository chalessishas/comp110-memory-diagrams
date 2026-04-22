"""Cardigan (卡缇) — 4★ Defender (Protector).

S1 "Regeneration α" (shared skcom_heal_self[1]):
  sp_cost=20, initial_sp=10, duration=0s (instant heal, not modeled — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.ardign import make_ardign as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "ardign_s1_regen"
_S1_DURATION = 0.0


def make_ardign(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Ardign"
    op.archetype = RoleArchetype.DEF_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Regeneration α", slot="S1", sp_cost=20, initial_sp=10,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
