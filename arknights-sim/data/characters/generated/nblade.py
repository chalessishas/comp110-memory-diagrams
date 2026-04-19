"""夜刀 — generated from ArknightsGameData char_502_nblade.
Source: E0 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_502_nblade
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_nblade() -> UnitState:
    return UnitState(
        name='夜刀',
        faction=Faction.ALLY,
        max_hp=1030,
        atk=262,
        defence=192,
        res=0.0,
        atk_interval=1.05,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=7,
        redeploy_cd=70.0,
    )
