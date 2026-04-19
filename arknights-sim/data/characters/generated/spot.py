"""斑点 — generated from ArknightsGameData char_284_spot.
Source: E1 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_284_spot
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_spot() -> UnitState:
    return UnitState(
        name='斑点',
        faction=Faction.ALLY,
        max_hp=1833,
        atk=350,
        defence=472,
        res=10.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=17,
        redeploy_cd=70.0,
    )
