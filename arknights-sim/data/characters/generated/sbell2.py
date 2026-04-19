"""圣聆初雪 — generated from ArknightsGameData char_1046_sbell2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1046_sbell2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_sbell2() -> UnitState:
    return UnitState(
        name='圣聆初雪',
        faction=Faction.ALLY,
        max_hp=2058,
        atk=916,
        defence=295,
        res=15.0,
        atk_interval=2.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=24,
        redeploy_cd=70.0,
    )
