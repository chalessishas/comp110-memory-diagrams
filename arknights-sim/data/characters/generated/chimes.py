"""铎铃 — generated from ArknightsGameData char_4083_chimes.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4083_chimes
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_chimes() -> UnitState:
    return UnitState(
        name='铎铃',
        faction=Faction.ALLY,
        max_hp=6019,
        atk=1508,
        defence=0,
        res=0.0,
        atk_interval=2.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=23,
        redeploy_cd=70.0,
    )
