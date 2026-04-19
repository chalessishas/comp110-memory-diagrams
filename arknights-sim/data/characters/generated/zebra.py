"""暴雨 — generated from ArknightsGameData char_304_zebra.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_304_zebra
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_zebra() -> UnitState:
    return UnitState(
        name='暴雨',
        faction=Faction.ALLY,
        max_hp=3730,
        atk=378,
        defence=756,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=24,
        redeploy_cd=80.0,
    )
