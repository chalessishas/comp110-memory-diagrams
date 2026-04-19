"""斩业星熊 — generated from ArknightsGameData char_1044_hsgma2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1044_hsgma2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_hsgma2() -> UnitState:
    return UnitState(
        name='斩业星熊',
        faction=Faction.ALLY,
        max_hp=3551,
        atk=722,
        defence=616,
        res=15.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.ARTS,
        block=3,
        cost=26,
        redeploy_cd=70.0,
    )
