"""幽灵鲨 — generated from ArknightsGameData char_143_ghost.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_143_ghost
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_ghost() -> UnitState:
    return UnitState(
        name='幽灵鲨',
        faction=Faction.ALLY,
        max_hp=2630,
        atk=805,
        defence=355,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=23,
        redeploy_cd=70.0,
    )
