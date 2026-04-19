"""格拉尼 — generated from ArknightsGameData char_220_grani.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_220_grani
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_grani() -> UnitState:
    return UnitState(
        name='格拉尼',
        faction=Faction.ALLY,
        max_hp=2235,
        atk=552,
        defence=437,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=14,
        redeploy_cd=80.0,
    )
