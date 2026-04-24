"""Pinecn (Pinecone 松果) — 4★ Sniper (Deadeye).

S1: sp_cost=10, initial_sp=0, duration=9s, AUTO_TIME, MANUAL (stub).
S2: sp_cost=30, initial_sp=0, duration=20s, AUTO_TIME, AUTO (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.pinecn import make_pinecn as _base_stats

SNP_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 4) for dy in range(-1, 2)))
_S1_TAG = "pinecn_s1"; _S1_DURATION = 9.0
_S2_TAG = "pinecn_s2"; _S2_DURATION = 20.0

def make_pinecn(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Pinecone"
    op.archetype = RoleArchetype.SNIPER_DEADEYE
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Pinecone S1", slot="S1", sp_cost=10, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Pinecone S2", slot="S2", sp_cost=30, initial_sp=0,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
