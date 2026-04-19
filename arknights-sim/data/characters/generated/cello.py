"""塑心 — generated from ArknightsGameData char_245_cello.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_245_cello
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_cello() -> UnitState:
    return UnitState(
        name='塑心',
        faction=Faction.ALLY,
        max_hp=1501,
        atk=525,
        defence=109,
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
