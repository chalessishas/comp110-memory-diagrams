"""Castle-3 — generated from ArknightsGameData char_286_cast3.
Source: E0 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_286_cast3
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_cast3() -> UnitState:
    return UnitState(
        name='Castle-3',
        faction=Faction.ALLY,
        max_hp=1391,
        atk=413,
        defence=90,
        res=0.0,
        atk_interval=1.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=3,
        redeploy_cd=200.0,
    )
