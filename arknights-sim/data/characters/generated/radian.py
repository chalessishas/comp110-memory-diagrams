"""电弧 — generated from ArknightsGameData char_4195_radian.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4195_radian
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_radian() -> UnitState:
    return UnitState(
        name='电弧',
        faction=Faction.ALLY,
        max_hp=1369,
        atk=486,
        defence=163,
        res=20.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=12,
        redeploy_cd=70.0,
    )
