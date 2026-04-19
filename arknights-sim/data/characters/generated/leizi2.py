"""司霆惊蛰 — generated from ArknightsGameData char_1043_leizi2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1043_leizi2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_leizi2() -> UnitState:
    return UnitState(
        name='司霆惊蛰',
        faction=Faction.ALLY,
        max_hp=4223,
        atk=390,
        defence=491,
        res=15.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=12,
        redeploy_cd=70.0,
    )
