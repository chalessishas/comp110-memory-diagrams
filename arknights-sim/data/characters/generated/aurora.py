"""极光 — generated from ArknightsGameData char_422_aurora.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_422_aurora
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_aurora() -> UnitState:
    return UnitState(
        name='极光',
        faction=Faction.ALLY,
        max_hp=4027,
        atk=956,
        defence=695,
        res=0.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=32,
        redeploy_cd=70.0,
    )
