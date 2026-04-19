"""伊桑 — generated from ArknightsGameData char_355_ethan.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_355_ethan
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_ethan() -> UnitState:
    return UnitState(
        name='伊桑',
        faction=Faction.ALLY,
        max_hp=1980,
        atk=742,
        defence=337,
        res=30.0,
        atk_interval=3.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=0,
        cost=19,
        redeploy_cd=70.0,
    )
