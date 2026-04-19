"""耀骑士临光 — generated from ArknightsGameData char_1014_nearl2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1014_nearl2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_nearl2() -> UnitState:
    return UnitState(
        name='耀骑士临光',
        faction=Faction.ALLY,
        max_hp=3750,
        atk=1149,
        defence=295,
        res=0.0,
        atk_interval=1.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=19,
        redeploy_cd=70.0,
    )
