"""月见夜 — generated from ArknightsGameData char_283_midn.
Source: E1 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_283_midn
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_midn() -> UnitState:
    return UnitState(
        name='月见夜',
        faction=Faction.ALLY,
        max_hp=1653,
        atk=547,
        defence=282,
        res=10.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=16,
        redeploy_cd=70.0,
    )
