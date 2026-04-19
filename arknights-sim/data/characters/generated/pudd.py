"""布丁 — generated from ArknightsGameData char_4004_pudd.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4004_pudd
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_pudd() -> UnitState:
    return UnitState(
        name='布丁',
        faction=Faction.ALLY,
        max_hp=1326,
        atk=612,
        defence=108,
        res=20.0,
        atk_interval=2.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=31,
        redeploy_cd=70.0,
    )
