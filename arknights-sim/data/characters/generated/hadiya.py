"""哈蒂娅 — generated from ArknightsGameData char_394_hadiya.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_394_hadiya
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_hadiya() -> UnitState:
    return UnitState(
        name='哈蒂娅',
        faction=Faction.ALLY,
        max_hp=2895,
        atk=585,
        defence=393,
        res=10.0,
        atk_interval=1.25,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=10,
        redeploy_cd=70.0,
    )
