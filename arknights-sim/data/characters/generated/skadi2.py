"""浊心斯卡蒂 — generated from ArknightsGameData char_1012_skadi2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1012_skadi2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_skadi2() -> UnitState:
    return UnitState(
        name='浊心斯卡蒂',
        faction=Faction.ALLY,
        max_hp=1603,
        atk=418,
        defence=263,
        res=0.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=8,
        redeploy_cd=70.0,
    )
