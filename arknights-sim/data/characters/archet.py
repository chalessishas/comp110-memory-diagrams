"""Archetto (空弦) — 5★ Sniper (Deadeye).

S1 "Dispersing Arrows": sp_cost=4, initial_sp=0, instant, AUTO_ATTACK, AUTO (stub).
  Next attack 200% ATK + 150% ATK to ≤3 nearby enemies. Multi-target split not modeled.
S2 "Pursuing Arrows": sp_cost=12, initial_sp=0, instant, AUTO_TIME, MANUAL (stub).
  5-hit ricochet arrow 120% ATK each, 2 charges. Complex ricochet not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.archet import make_archet as _base_stats

SNP_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 4) for dy in range(-1, 2)))
_S1_TAG = "archet_s1"; _S1_DURATION = 0.0
_S2_TAG = "archet_s2"; _S2_DURATION = 0.0

def make_archet(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Archetto"
    op.archetype = RoleArchetype.SNIPER_DEADEYE
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Dispersing Arrows", slot="S1", sp_cost=4, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Pursuing Arrows", slot="S2", sp_cost=12, initial_sp=0,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
