"""THRM-EX — generated from ArknightsGameData char_376_therex.
Source: E0 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_376_therex
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_therex() -> UnitState:
    return UnitState(
        name='THRM-EX',
        faction=Faction.ALLY,
        max_hp=1443,
        atk=350,
        defence=443,
        res=50.0,
        atk_interval=0.93,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=0,
        cost=3,
        redeploy_cd=200.0,
    )
