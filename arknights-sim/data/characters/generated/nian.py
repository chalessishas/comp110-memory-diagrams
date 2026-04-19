"""年 — generated from ArknightsGameData char_2014_nian.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_2014_nian
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_nian() -> UnitState:
    return UnitState(
        name='年',
        faction=Faction.ALLY,
        max_hp=4099,
        atk=619,
        defence=796,
        res=0.0,
        atk_interval=1.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=23,
        redeploy_cd=70.0,
    )
