"""阿罗玛 — generated from ArknightsGameData char_446_aroma.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_446_aroma
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_aroma() -> UnitState:
    return UnitState(
        name='阿罗玛',
        faction=Faction.ALLY,
        max_hp=1651,
        atk=840,
        defence=115,
        res=20.0,
        atk_interval=2.9,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=33,
        redeploy_cd=70.0,
    )
