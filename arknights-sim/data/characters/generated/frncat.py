"""慕斯 — generated from ArknightsGameData char_185_frncat.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_185_frncat
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_frncat() -> UnitState:
    return UnitState(
        name='慕斯',
        faction=Faction.ALLY,
        max_hp=2345,
        atk=679,
        defence=392,
        res=15.0,
        atk_interval=1.25,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.ARTS,
        block=1,
        cost=20,
        redeploy_cd=70.0,
    )
