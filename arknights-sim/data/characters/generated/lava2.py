"""炎狱炎熔 — generated from ArknightsGameData char_1011_lava2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1011_lava2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_lava2() -> UnitState:
    return UnitState(
        name='炎狱炎熔',
        faction=Faction.ALLY,
        max_hp=1543,
        atk=888,
        defence=115,
        res=20.0,
        atk_interval=2.9,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=35,
        redeploy_cd=80.0,
    )
