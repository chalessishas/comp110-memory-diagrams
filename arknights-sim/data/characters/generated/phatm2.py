"""酒神 — generated from ArknightsGameData char_1042_phatm2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1042_phatm2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_phatm2() -> UnitState:
    return UnitState(
        name='酒神',
        faction=Faction.ALLY,
        max_hp=1500,
        atk=530,
        defence=104,
        res=15.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=16,
        redeploy_cd=70.0,
    )
