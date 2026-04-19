"""铸铁 — generated from ArknightsGameData char_333_sidero.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_333_sidero
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_sidero() -> UnitState:
    return UnitState(
        name='铸铁',
        faction=Faction.ALLY,
        max_hp=3345,
        atk=620,
        defence=369,
        res=15.0,
        atk_interval=1.25,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=23,
        redeploy_cd=80.0,
    )
