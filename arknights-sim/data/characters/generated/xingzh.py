"""行箸 — generated from ArknightsGameData char_4172_xingzh.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4172_xingzh
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_xingzh() -> UnitState:
    return UnitState(
        name='行箸',
        faction=Faction.ALLY,
        max_hp=1746,
        atk=473,
        defence=231,
        res=25.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=13,
        redeploy_cd=80.0,
    )
