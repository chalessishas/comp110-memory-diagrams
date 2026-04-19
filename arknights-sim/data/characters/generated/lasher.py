"""衡沙 — generated from ArknightsGameData char_4140_lasher.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4140_lasher
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_lasher() -> UnitState:
    return UnitState(
        name='衡沙',
        faction=Faction.ALLY,
        max_hp=1231,
        atk=485,
        defence=160,
        res=20.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=11,
        redeploy_cd=70.0,
    )
