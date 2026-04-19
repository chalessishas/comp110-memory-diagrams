"""维娜·维多利亚 — generated from ArknightsGameData char_1019_siege2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1019_siege2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_siege2() -> UnitState:
    return UnitState(
        name='维娜·维多利亚',
        faction=Faction.ALLY,
        max_hp=2895,
        atk=745,
        defence=450,
        res=15.0,
        atk_interval=1.25,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=21,
        redeploy_cd=70.0,
    )
