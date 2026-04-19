"""休谟斯 — generated from ArknightsGameData char_491_humus.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_491_humus
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_humus() -> UnitState:
    return UnitState(
        name='休谟斯',
        faction=Faction.ALLY,
        max_hp=2150,
        atk=646,
        defence=433,
        res=0.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=21,
        redeploy_cd=70.0,
    )
