"""耶拉 — generated from ArknightsGameData char_4013_kjera.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4013_kjera
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_kjera() -> UnitState:
    return UnitState(
        name='耶拉',
        faction=Faction.ALLY,
        max_hp=1475,
        atk=354,
        defence=121,
        res=20.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=23,
        redeploy_cd=80.0,
    )
