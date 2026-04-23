"""Catapult (投石手) — 3★ Sniper (Artilleryman).

S1 "Blast Range Up α": sp_cost=45, initial_sp=0, duration=30s (splash_radius ×2 stub;
  base splash_radius=0.0 in generated data, mutation cannot be applied meaningfully).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.catap import make_catap as _base_stats

ARTILLERY_RANGE = RangeShape(tiles=tuple(
    (dx, dy)
    for dx in range(1, 6)
    for dy in range(-1, 2)
))

_S1_TAG = "catap_s1_blast_range_up"
_S1_DURATION = 30.0


def make_catap(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Catap"
    op.archetype = RoleArchetype.SNIPER_ARTILLERY
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = ARTILLERY_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Blast Range Up α", slot="S1", sp_cost=45, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
