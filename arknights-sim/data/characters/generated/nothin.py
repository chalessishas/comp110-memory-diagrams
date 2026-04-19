"""乌有 — generated from ArknightsGameData char_455_nothin.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_455_nothin
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_nothin() -> UnitState:
    return UnitState(
        name='乌有',
        faction=Faction.ALLY,
        max_hp=2598,
        atk=765,
        defence=396,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=8,
        redeploy_cd=25.0,
    )
