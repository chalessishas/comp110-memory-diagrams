"""W — generated from ArknightsGameData char_113_cqbw.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_113_cqbw
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_cqbw() -> UnitState:
    return UnitState(
        name='W',
        faction=Faction.ALLY,
        max_hp=1605,
        atk=1012,
        defence=133,
        res=0.0,
        atk_interval=2.8,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=29,
        redeploy_cd=70.0,
    )
