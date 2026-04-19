"""八幡海铃 — generated from ArknightsGameData char_4186_tmoris.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4186_tmoris
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_tmoris() -> UnitState:
    return UnitState(
        name='八幡海铃',
        faction=Faction.ALLY,
        max_hp=1929,
        atk=839,
        defence=361,
        res=30.0,
        atk_interval=3.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=0,
        cost=22,
        redeploy_cd=80.0,
    )
