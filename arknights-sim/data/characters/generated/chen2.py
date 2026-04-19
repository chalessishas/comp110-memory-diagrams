"""假日威龙陈 — generated from ArknightsGameData char_1013_chen2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1013_chen2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_chen2() -> UnitState:
    return UnitState(
        name='假日威龙陈',
        faction=Faction.ALLY,
        max_hp=2501,
        atk=853,
        defence=203,
        res=0.0,
        atk_interval=2.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=32,
        redeploy_cd=70.0,
    )
