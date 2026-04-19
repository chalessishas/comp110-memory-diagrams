"""炎熔 — generated from ArknightsGameData char_121_lava.
Source: E1 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_121_lava
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_lava() -> UnitState:
    return UnitState(
        name='炎熔',
        faction=Faction.ALLY,
        max_hp=1141,
        atk=642,
        defence=95,
        res=15.0,
        atk_interval=2.9,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=30,
        redeploy_cd=70.0,
    )
