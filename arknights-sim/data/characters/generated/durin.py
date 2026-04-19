"""杜林 — generated from ArknightsGameData char_501_durin.
Source: E0 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_501_durin
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_durin() -> UnitState:
    return UnitState(
        name='杜林',
        faction=Faction.ALLY,
        max_hp=952,
        atk=370,
        defence=62,
        res=10.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=12,
        redeploy_cd=70.0,
    )
