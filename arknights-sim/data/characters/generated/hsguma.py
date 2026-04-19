"""星熊 — generated from ArknightsGameData char_136_hsguma.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_136_hsguma
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_hsguma() -> UnitState:
    return UnitState(
        name='星熊',
        faction=Faction.ALLY,
        max_hp=3850,
        atk=490,
        defence=783,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=23,
        redeploy_cd=70.0,
    )
