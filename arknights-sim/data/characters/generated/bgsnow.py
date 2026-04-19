"""鸿雪 — generated from ArknightsGameData char_4055_bgsnow.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4055_bgsnow
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_bgsnow() -> UnitState:
    return UnitState(
        name='鸿雪',
        faction=Faction.ALLY,
        max_hp=1802,
        atk=946,
        defence=223,
        res=0.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=20,
        redeploy_cd=70.0,
    )
