"""凯瑟琳 — generated from ArknightsGameData char_4162_cathy.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4162_cathy
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_cathy() -> UnitState:
    return UnitState(
        name='凯瑟琳',
        faction=Faction.ALLY,
        max_hp=2680,
        atk=590,
        defence=460,
        res=0.0,
        atk_interval=1.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=2,
        cost=20,
        redeploy_cd=80.0,
    )
