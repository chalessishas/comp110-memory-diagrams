"""因陀罗 — generated from ArknightsGameData char_155_tiger.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_155_tiger
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_tiger() -> UnitState:
    return UnitState(
        name='因陀罗',
        faction=Faction.ALLY,
        max_hp=2565,
        atk=605,
        defence=350,
        res=0.0,
        atk_interval=0.78,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=10,
        redeploy_cd=70.0,
    )
