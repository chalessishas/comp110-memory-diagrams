"""Friston-3 — generated from ArknightsGameData char_4093_frston.
Source: E0 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4093_frston
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_frston() -> UnitState:
    return UnitState(
        name='Friston-3',
        faction=Faction.ALLY,
        max_hp=1252,
        atk=198,
        defence=305,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=3,
        redeploy_cd=200.0,
    )
