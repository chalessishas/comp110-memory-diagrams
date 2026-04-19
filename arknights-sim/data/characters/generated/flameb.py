"""炎客 — generated from ArknightsGameData char_131_flameb.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_131_flameb
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_flameb() -> UnitState:
    return UnitState(
        name='炎客',
        faction=Faction.ALLY,
        max_hp=4307,
        atk=963,
        defence=195,
        res=0.0,
        atk_interval=1.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=20,
        redeploy_cd=80.0,
    )
