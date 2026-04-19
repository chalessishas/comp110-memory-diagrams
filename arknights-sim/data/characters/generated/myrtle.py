"""桃金娘 — generated from ArknightsGameData char_151_myrtle.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_151_myrtle
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_myrtle() -> UnitState:
    return UnitState(
        name='桃金娘',
        faction=Faction.ALLY,
        max_hp=1565,
        atk=520,
        defence=350,
        res=0.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=10,
        redeploy_cd=70.0,
    )
