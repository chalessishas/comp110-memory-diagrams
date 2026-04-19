"""和弦 — generated from ArknightsGameData char_297_hamoni.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_297_hamoni
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_hamoni() -> UnitState:
    return UnitState(
        name='和弦',
        faction=Faction.ALLY,
        max_hp=1546,
        atk=1375,
        defence=125,
        res=20.0,
        atk_interval=3.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=24,
        redeploy_cd=70.0,
    )
