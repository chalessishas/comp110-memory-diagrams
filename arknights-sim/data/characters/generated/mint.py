"""薄绿 — generated from ArknightsGameData char_388_mint.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_388_mint
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_mint() -> UnitState:
    return UnitState(
        name='薄绿',
        faction=Faction.ALLY,
        max_hp=1945,
        atk=807,
        defence=211,
        res=15.0,
        atk_interval=2.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=25,
        redeploy_cd=80.0,
    )
