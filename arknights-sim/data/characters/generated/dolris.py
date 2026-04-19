"""三角初华 — generated from ArknightsGameData char_4184_dolris.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4184_dolris
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_dolris() -> UnitState:
    return UnitState(
        name='三角初华',
        faction=Faction.ALLY,
        max_hp=1410,
        atk=379,
        defence=253,
        res=0.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=7,
        redeploy_cd=70.0,
    )
