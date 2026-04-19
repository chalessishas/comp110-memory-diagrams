"""褐果 — generated from ArknightsGameData char_4041_chnut.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4041_chnut
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_chnut() -> UnitState:
    return UnitState(
        name='褐果',
        faction=Faction.ALLY,
        max_hp=1237,
        atk=424,
        defence=101,
        res=10.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=14,
        redeploy_cd=70.0,
    )
