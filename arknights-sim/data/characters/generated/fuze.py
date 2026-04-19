"""导火索 — generated from ArknightsGameData char_4126_fuze.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4126_fuze
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_fuze() -> UnitState:
    return UnitState(
        name='导火索',
        faction=Faction.ALLY,
        max_hp=2660,
        atk=835,
        defence=330,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=25,
        redeploy_cd=80.0,
    )
