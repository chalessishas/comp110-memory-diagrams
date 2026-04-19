"""初雪 — generated from ArknightsGameData char_174_slbell.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_174_slbell
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_slbell() -> UnitState:
    return UnitState(
        name='初雪',
        faction=Faction.ALLY,
        max_hp=1605,
        atk=495,
        defence=102,
        res=25.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=12,
        redeploy_cd=70.0,
    )
