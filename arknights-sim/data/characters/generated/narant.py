"""娜仁图亚 — generated from ArknightsGameData char_4138_narant.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4138_narant
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_narant() -> UnitState:
    return UnitState(
        name='娜仁图亚',
        faction=Faction.ALLY,
        max_hp=2500,
        atk=765,
        defence=170,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=16,
        redeploy_cd=70.0,
    )
