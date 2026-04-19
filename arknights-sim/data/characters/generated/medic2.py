"""Lancet-2 — generated from ArknightsGameData char_285_medic2.
Source: E0 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_285_medic2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_medic2() -> UnitState:
    return UnitState(
        name='Lancet-2',
        faction=Faction.ALLY,
        max_hp=535,
        atk=110,
        defence=27,
        res=0.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=3,
        redeploy_cd=200.0,
    )
