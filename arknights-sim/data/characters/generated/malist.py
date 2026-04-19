"""至简 — generated from ArknightsGameData char_4054_malist.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4054_malist
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_malist() -> UnitState:
    return UnitState(
        name='至简',
        faction=Faction.ALLY,
        max_hp=1500,
        atk=360,
        defence=120,
        res=20.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=23,
        redeploy_cd=80.0,
    )
