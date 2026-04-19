"""巡林者 — generated from ArknightsGameData char_503_rang.
Source: E0 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_503_rang
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_rang() -> UnitState:
    return UnitState(
        name='巡林者',
        faction=Faction.ALLY,
        max_hp=780,
        atk=299,
        defence=66,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=7,
        redeploy_cd=70.0,
    )
