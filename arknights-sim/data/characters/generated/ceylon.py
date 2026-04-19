"""锡兰 — generated from ArknightsGameData char_348_ceylon.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_348_ceylon
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_ceylon() -> UnitState:
    return UnitState(
        name='锡兰',
        faction=Faction.ALLY,
        max_hp=1655,
        atk=508,
        defence=126,
        res=10.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=22,
        redeploy_cd=80.0,
    )
