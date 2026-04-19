"""承曦格雷伊 — generated from ArknightsGameData char_1027_greyy2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1027_greyy2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_greyy2() -> UnitState:
    return UnitState(
        name='承曦格雷伊',
        faction=Faction.ALLY,
        max_hp=1880,
        atk=688,
        defence=240,
        res=15.0,
        atk_interval=2.1,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=24,
        redeploy_cd=70.0,
    )
