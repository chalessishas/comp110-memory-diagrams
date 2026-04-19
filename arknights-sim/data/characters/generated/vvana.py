"""薇薇安娜 — generated from ArknightsGameData char_4098_vvana.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4098_vvana
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_vvana() -> UnitState:
    return UnitState(
        name='薇薇安娜',
        faction=Faction.ALLY,
        max_hp=2920,
        atk=746,
        defence=447,
        res=15.0,
        atk_interval=1.25,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.ARTS,
        block=1,
        cost=21,
        redeploy_cd=70.0,
    )
