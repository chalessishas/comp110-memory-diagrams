"""濯尘芙蓉 — generated from ArknightsGameData char_1024_hbisc2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1024_hbisc2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_hbisc2() -> UnitState:
    return UnitState(
        name='濯尘芙蓉',
        faction=Faction.ALLY,
        max_hp=1508,
        atk=571,
        defence=109,
        res=20.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=17,
        redeploy_cd=70.0,
    )
