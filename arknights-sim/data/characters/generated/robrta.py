"""罗比菈塔 — generated from ArknightsGameData char_484_robrta.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_484_robrta
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_robrta() -> UnitState:
    return UnitState(
        name='罗比菈塔',
        faction=Faction.ALLY,
        max_hp=2470,
        atk=570,
        defence=450,
        res=0.0,
        atk_interval=1.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=2,
        cost=17,
        redeploy_cd=70.0,
    )
