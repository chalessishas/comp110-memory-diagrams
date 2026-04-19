"""焰影苇草 — generated from ArknightsGameData char_1020_reed2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1020_reed2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_reed2() -> UnitState:
    return UnitState(
        name='焰影苇草',
        faction=Faction.ALLY,
        max_hp=1583,
        atk=600,
        defence=114,
        res=20.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=17,
        redeploy_cd=70.0,
    )
