"""协律 — generated from ArknightsGameData char_4051_akkord.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4051_akkord
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_akkord() -> UnitState:
    return UnitState(
        name='协律',
        faction=Faction.ALLY,
        max_hp=1528,
        atk=740,
        defence=110,
        res=20.0,
        atk_interval=2.9,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=32,
        redeploy_cd=70.0,
    )
