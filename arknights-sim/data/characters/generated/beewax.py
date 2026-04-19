"""蜜蜡 — generated from ArknightsGameData char_344_beewax.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_344_beewax
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_beewax() -> UnitState:
    return UnitState(
        name='蜜蜡',
        faction=Faction.ALLY,
        max_hp=2005,
        atk=805,
        defence=225,
        res=15.0,
        atk_interval=2.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=23,
        redeploy_cd=70.0,
    )
