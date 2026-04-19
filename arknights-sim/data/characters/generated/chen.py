"""陈 — generated from ArknightsGameData char_010_chen.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_010_chen
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_chen() -> UnitState:
    return UnitState(
        name='陈',
        faction=Faction.ALLY,
        max_hp=2880,
        atk=660,
        defence=402,
        res=0.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=23,
        redeploy_cd=70.0,
    )
