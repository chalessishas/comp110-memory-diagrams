"""芬 — generated from ArknightsGameData char_123_fang.
Source: E1 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_123_fang
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_fang() -> UnitState:
    return UnitState(
        name='芬',
        faction=Faction.ALLY,
        max_hp=1325,
        atk=325,
        defence=310,
        res=0.0,
        atk_interval=1.05,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=11,
        redeploy_cd=70.0,
    )
