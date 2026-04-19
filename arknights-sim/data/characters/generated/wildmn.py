"""野鬃 — generated from ArknightsGameData char_496_wildmn.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_496_wildmn
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_wildmn() -> UnitState:
    return UnitState(
        name='野鬃',
        faction=Faction.ALLY,
        max_hp=2225,
        atk=628,
        defence=372,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=14,
        redeploy_cd=80.0,
    )
