"""雪绒 — generated from ArknightsGameData char_466_qanik.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_466_qanik
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_qanik() -> UnitState:
    return UnitState(
        name='雪绒',
        faction=Faction.ALLY,
        max_hp=1500,
        atk=695,
        defence=119,
        res=20.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=20,
        redeploy_cd=70.0,
    )
