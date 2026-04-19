"""令 — generated from ArknightsGameData char_2023_ling.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_2023_ling
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_ling() -> UnitState:
    return UnitState(
        name='令',
        faction=Faction.ALLY,
        max_hp=1429,
        atk=508,
        defence=138,
        res=20.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=12,
        redeploy_cd=70.0,
    )
