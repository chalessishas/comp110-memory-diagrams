"""清流 — generated from ArknightsGameData char_385_finlpp.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_385_finlpp
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_finlpp() -> UnitState:
    return UnitState(
        name='清流',
        faction=Faction.ALLY,
        max_hp=1515,
        atk=489,
        defence=118,
        res=10.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=19,
        redeploy_cd=80.0,
    )
