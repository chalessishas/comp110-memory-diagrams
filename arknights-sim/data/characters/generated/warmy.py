"""温米 — generated from ArknightsGameData char_4081_warmy.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4081_warmy
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_warmy() -> UnitState:
    return UnitState(
        name='温米',
        faction=Faction.ALLY,
        max_hp=1358,
        atk=646,
        defence=106,
        res=15.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=20,
        redeploy_cd=70.0,
    )
