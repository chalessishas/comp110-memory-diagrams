"""琳琅诗怀雅 — generated from ArknightsGameData char_1033_swire2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1033_swire2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_swire2() -> UnitState:
    return UnitState(
        name='琳琅诗怀雅',
        faction=Faction.ALLY,
        max_hp=2660,
        atk=865,
        defence=457,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=9,
        redeploy_cd=25.0,
    )
