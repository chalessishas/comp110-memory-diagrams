"""U-Official — generated from ArknightsGameData char_4091_ulika.
Source: E0 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4091_ulika
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_ulika() -> UnitState:
    return UnitState(
        name='U-Official',
        faction=Faction.ALLY,
        max_hp=505,
        atk=122,
        defence=28,
        res=0.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=3,
        redeploy_cd=200.0,
    )
