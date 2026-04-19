"""CONFESS-47 — generated from ArknightsGameData char_4188_confes.
Source: E0 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4188_confes
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_confes() -> UnitState:
    return UnitState(
        name='CONFESS-47',
        faction=Faction.ALLY,
        max_hp=870,
        atk=192,
        defence=184,
        res=0.0,
        atk_interval=1.05,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=3,
        redeploy_cd=200.0,
    )
