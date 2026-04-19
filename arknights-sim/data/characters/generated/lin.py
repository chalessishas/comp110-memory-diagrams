"""林 — generated from ArknightsGameData char_4080_lin.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4080_lin
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_lin() -> UnitState:
    return UnitState(
        name='林',
        faction=Faction.ALLY,
        max_hp=2048,
        atk=919,
        defence=282,
        res=15.0,
        atk_interval=2.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=24,
        redeploy_cd=70.0,
    )
