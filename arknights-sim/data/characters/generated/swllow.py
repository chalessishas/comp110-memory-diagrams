"""灰喉 — generated from ArknightsGameData char_367_swllow.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_367_swllow
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_swllow() -> UnitState:
    return UnitState(
        name='灰喉',
        faction=Faction.ALLY,
        max_hp=1493,
        atk=588,
        defence=152,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=13,
        redeploy_cd=70.0,
    )
