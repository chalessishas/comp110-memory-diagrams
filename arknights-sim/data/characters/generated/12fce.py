"""12F — generated from ArknightsGameData char_009_12fce.
Source: E0 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_009_12fce
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_12fce() -> UnitState:
    return UnitState(
        name='12F',
        faction=Faction.ALLY,
        max_hp=1461,
        atk=482,
        defence=50,
        res=10.0,
        atk_interval=2.9,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=24,
        redeploy_cd=70.0,
    )
