"""Muelsyse (缪尔赛思) — 6★ Vanguard (Tactician).

All skills involve DP mechanics or summon clones — behavior not modeled.

S1: sp_cost=32, initial_sp=8, duration=15s, AUTO_TIME, MANUAL (stub).
S2: sp_cost=39, initial_sp=15, duration=15s, AUTO_TIME, MANUAL (stub).
S3: sp_cost=39, initial_sp=15, duration=15s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.mlyss import make_mlyss as _base_stats

VAN_RANGE = RangeShape(tiles=((0, 0), (1, 0)))
_S1_TAG = "mlyss_s1"; _S1_DURATION = 15.0
_S2_TAG = "mlyss_s2"; _S2_DURATION = 15.0
_S3_TAG = "mlyss_s3"; _S3_DURATION = 15.0


def make_mlyss(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Mlyss"
    op.archetype = RoleArchetype.VAN_TACTICIAN
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = VAN_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Mlyss S1", slot="S1", sp_cost=32, initial_sp=8,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Mlyss S2", slot="S2", sp_cost=39, initial_sp=15,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    elif slot == "S3":
        op.skill = SkillComponent(name="Mlyss S3", slot="S3", sp_cost=39, initial_sp=15,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
