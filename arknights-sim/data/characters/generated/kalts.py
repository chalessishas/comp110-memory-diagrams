"""凯尔希 — generated from ArknightsGameData char_003_kalts.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_003_kalts
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_kalts() -> UnitState:
    return UnitState(
        name='凯尔希',
        faction=Faction.ALLY,
        max_hp=2033,
        atk=490,
        defence=255,
        res=0.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=20,
        redeploy_cd=70.0,
    )
