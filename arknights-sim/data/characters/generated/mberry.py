"""桑葚 — generated from ArknightsGameData char_473_mberry.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_473_mberry
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_mberry() -> UnitState:
    return UnitState(
        name='桑葚',
        faction=Faction.ALLY,
        max_hp=1517,
        atk=423,
        defence=99,
        res=10.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=15,
        redeploy_cd=70.0,
    )
