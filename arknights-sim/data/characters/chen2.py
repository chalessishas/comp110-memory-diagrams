"""Ch'en the Holungday (假日威龙陈) — 6★ Limited Sniper (Spreadshooter).

S1 "High-Pressure Splash": sp_cost=5, initial_sp=0, ammo-based (stub).
S2 "Night of Violet": sp_cost=24, initial_sp=10, ammo-based + goo terrain (stub).
S3 "Holiday Storm": sp_cost=60, initial_sp=25, ammo-based + double-hit + goo (stub).

All skills use ammo mechanic; none are modeled as sustained buffs.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.chen2 import make_chen2 as _base_stats

SNIPER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0), (4, 0),
    (1, -1), (2, -1), (3, -1),
    (1, 1), (2, 1), (3, 1),
))

_S1_TAG = "chen2_s1_high_pressure_splash"
_S2_TAG = "chen2_s2_night_of_violet"
_S3_TAG = "chen2_s3_holiday_storm"


def make_chen2(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Ch'en HD"
    op.archetype = RoleArchetype.SNIPER_MARKSMAN
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNIPER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="High-Pressure Splash", slot="S1", sp_cost=5, initial_sp=0,
            duration=0.0, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Night of Violet", slot="S2", sp_cost=24, initial_sp=10,
            duration=0.0, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Holiday Storm", slot="S3", sp_cost=60, initial_sp=25,
            duration=0.0, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
