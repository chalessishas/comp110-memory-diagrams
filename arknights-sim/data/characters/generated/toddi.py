"""熔泉 — generated from ArknightsGameData char_363_toddi.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_363_toddi
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_toddi() -> UnitState:
    return UnitState(
        name='熔泉',
        faction=Faction.ALLY,
        max_hp=1667,
        atk=1049,
        defence=123,
        res=0.0,
        atk_interval=2.4,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=23,
        redeploy_cd=70.0,
    )
