"""隐德来希 — generated from ArknightsGameData char_4010_etlchi.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4010_etlchi
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_etlchi() -> UnitState:
    return UnitState(
        name='隐德来希',
        faction=Faction.ALLY,
        max_hp=2580,
        atk=750,
        defence=502,
        res=0.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=23,
        redeploy_cd=70.0,
    )
