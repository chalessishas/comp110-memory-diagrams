"""玫兰莎 — generated from ArknightsGameData char_208_melan.
Source: E1 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_208_melan
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_melan() -> UnitState:
    return UnitState(
        name='玫兰莎',
        faction=Faction.ALLY,
        max_hp=2745,
        atk=803,
        defence=155,
        res=0.0,
        atk_interval=1.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=15,
        redeploy_cd=70.0,
    )
