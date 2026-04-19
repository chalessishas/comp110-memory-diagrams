"""黑键 — generated from ArknightsGameData char_4046_ebnhlz.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4046_ebnhlz
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_ebnhlz() -> UnitState:
    return UnitState(
        name='黑键',
        faction=Faction.ALLY,
        max_hp=1678,
        atk=1550,
        defence=135,
        res=20.0,
        atk_interval=3.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=25,
        redeploy_cd=70.0,
    )
