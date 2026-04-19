"""琴柳 — generated from ArknightsGameData char_479_sleach.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_479_sleach
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_sleach() -> UnitState:
    return UnitState(
        name='琴柳',
        faction=Faction.ALLY,
        max_hp=1835,
        atk=586,
        defence=407,
        res=0.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=12,
        redeploy_cd=70.0,
    )
