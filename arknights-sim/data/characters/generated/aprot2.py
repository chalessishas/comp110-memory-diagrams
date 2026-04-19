"""暮落 — generated from ArknightsGameData char_4025_aprot2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4025_aprot2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_aprot2() -> UnitState:
    return UnitState(
        name='暮落',
        faction=Faction.ALLY,
        max_hp=3090,
        atk=729,
        defence=550,
        res=15.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.ARTS,
        block=3,
        cost=25,
        redeploy_cd=70.0,
    )
