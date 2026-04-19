"""史尔特尔 — generated from ArknightsGameData char_350_surtr.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_350_surtr
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_surtr() -> UnitState:
    return UnitState(
        name='史尔特尔',
        faction=Faction.ALLY,
        max_hp=2916,
        atk=772,
        defence=414,
        res=15.0,
        atk_interval=1.25,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.ARTS,
        block=1,
        cost=21,
        redeploy_cd=70.0,
    )
