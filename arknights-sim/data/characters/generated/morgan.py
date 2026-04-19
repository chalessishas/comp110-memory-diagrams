"""摩根 — generated from ArknightsGameData char_154_morgan.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_154_morgan
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_morgan() -> UnitState:
    return UnitState(
        name='摩根',
        faction=Faction.ALLY,
        max_hp=3810,
        atk=980,
        defence=268,
        res=0.0,
        atk_interval=1.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=20,
        redeploy_cd=80.0,
    )
