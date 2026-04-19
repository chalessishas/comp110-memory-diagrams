"""锡人 — generated from ArknightsGameData char_4151_tinman.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4151_tinman
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_tinman() -> UnitState:
    return UnitState(
        name='锡人',
        faction=Faction.ALLY,
        max_hp=1314,
        atk=499,
        defence=99,
        res=30.0,
        atk_interval=1.5,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=17,
        redeploy_cd=70.0,
    )
