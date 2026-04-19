"""帕拉斯 — generated from ArknightsGameData char_485_pallas.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_485_pallas
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_pallas() -> UnitState:
    return UnitState(
        name='帕拉斯',
        faction=Faction.ALLY,
        max_hp=2263,
        atk=737,
        defence=455,
        res=0.0,
        atk_interval=1.05,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=17,
        redeploy_cd=70.0,
    )
