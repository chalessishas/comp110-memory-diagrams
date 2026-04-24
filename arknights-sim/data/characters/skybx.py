"""Skybox (天空盒) — 5★ Sniper (Skybreaker branch; modeled as Deadeye — no Skybreaker type).

SKIP: both skills are ammo/charge-based, cannot model as simple ATK buff.
S1 "Originium Gunpowder": sp_cost=9, initial_sp=0, ammo=2, 240% ATK AoE each.
S2 "Electromagnetic Pulse": sp_cost=30, initial_sp=16, ammo=10, ATK×180%/shot + Overload dump.
S3: does not exist (5★ operator).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.skybx import make_skybx as _base_stats

SNP_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 4) for dy in range(-1, 2)))
_S1_TAG = "skybx_s1"; _S1_DURATION = 0.0
_S2_TAG = "skybx_s2"; _S2_DURATION = 20.0
_S3_TAG = "skybx_s3"; _S3_DURATION = 25.0

def make_skybx(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Skybx"
    op.archetype = RoleArchetype.SNIPER_DEADEYE
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Originium Gunpowder", slot="S1", sp_cost=9, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Electromagnetic Pulse", slot="S2", sp_cost=30, initial_sp=16,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    elif slot == "S3":
        op.skill = SkillComponent(name="Skybx S3", slot="S3", sp_cost=70, initial_sp=35,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
