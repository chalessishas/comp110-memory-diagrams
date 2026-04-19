"""号角 — generated from ArknightsGameData char_4039_horn.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4039_horn
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_horn() -> UnitState:
    return UnitState(
        name='号角',
        faction=Faction.ALLY,
        max_hp=3367,
        atk=1006,
        defence=620,
        res=0.0,
        atk_interval=2.8,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=28,
        redeploy_cd=70.0,
    )
