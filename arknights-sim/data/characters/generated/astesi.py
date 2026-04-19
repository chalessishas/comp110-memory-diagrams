"""星极 — generated from ArknightsGameData char_274_astesi.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_274_astesi
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_astesi() -> UnitState:
    return UnitState(
        name='星极',
        faction=Faction.ALLY,
        max_hp=2523,
        atk=690,
        defence=448,
        res=15.0,
        atk_interval=1.25,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.ARTS,
        block=1,
        cost=21,
        redeploy_cd=70.0,
    )
