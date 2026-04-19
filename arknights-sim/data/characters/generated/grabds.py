"""小满 — generated from ArknightsGameData char_4122_grabds.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4122_grabds
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_grabds() -> UnitState:
    return UnitState(
        name='小满',
        faction=Faction.ALLY,
        max_hp=1260,
        atk=590,
        defence=100,
        res=20.0,
        atk_interval=1.9,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=15,
        redeploy_cd=70.0,
    )
