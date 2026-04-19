"""骋风 — generated from ArknightsGameData char_445_wscoot.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_445_wscoot
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_wscoot() -> UnitState:
    return UnitState(
        name='骋风',
        faction=Faction.ALLY,
        max_hp=3655,
        atk=320,
        defence=486,
        res=15.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=10,
        redeploy_cd=70.0,
    )
