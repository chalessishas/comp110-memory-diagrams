"""复奏 — generated from ArknightsGameData char_4031_liesel.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4031_liesel
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_liesel() -> UnitState:
    return UnitState(
        name='复奏',
        faction=Faction.ALLY,
        max_hp=1550,
        atk=875,
        defence=125,
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
