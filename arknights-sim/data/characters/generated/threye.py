"""凛视 — generated from ArknightsGameData char_4102_threye.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4102_threye
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_threye() -> UnitState:
    return UnitState(
        name='凛视',
        faction=Faction.ALLY,
        max_hp=1347,
        atk=477,
        defence=101,
        res=15.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=15,
        redeploy_cd=70.0,
    )
