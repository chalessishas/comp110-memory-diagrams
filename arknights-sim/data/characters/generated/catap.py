"""空爆 — generated from ArknightsGameData char_282_catap.
Source: E1 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_282_catap
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_catap() -> UnitState:
    return UnitState(
        name='空爆',
        faction=Faction.ALLY,
        max_hp=1150,
        atk=672,
        defence=85,
        res=0.0,
        atk_interval=2.8,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=23,
        redeploy_cd=70.0,
    )
