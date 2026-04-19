"""罗宾 — generated from ArknightsGameData char_451_robin.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_451_robin
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_robin() -> UnitState:
    return UnitState(
        name='罗宾',
        faction=Faction.ALLY,
        max_hp=1642,
        atk=553,
        defence=166,
        res=0.0,
        atk_interval=0.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=13,
        redeploy_cd=80.0,
    )
