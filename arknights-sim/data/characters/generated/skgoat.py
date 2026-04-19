"""地灵 — generated from ArknightsGameData char_183_skgoat.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_183_skgoat
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_skgoat() -> UnitState:
    return UnitState(
        name='地灵',
        faction=Faction.ALLY,
        max_hp=1205,
        atk=530,
        defence=101,
        res=20.0,
        atk_interval=1.9,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=14,
        redeploy_cd=70.0,
    )
