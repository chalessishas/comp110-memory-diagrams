"""伺夜 — generated from ArknightsGameData char_427_vigil.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_427_vigil
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_vigil() -> UnitState:
    return UnitState(
        name='伺夜',
        faction=Faction.ALLY,
        max_hp=1755,
        atk=542,
        defence=154,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=17,
        redeploy_cd=70.0,
    )
