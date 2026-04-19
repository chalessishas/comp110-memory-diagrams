"""闪击 — generated from ArknightsGameData char_457_blitz.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_457_blitz
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_blitz() -> UnitState:
    return UnitState(
        name='闪击',
        faction=Faction.ALLY,
        max_hp=3213,
        atk=490,
        defence=721,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=22,
        redeploy_cd=70.0,
    )
