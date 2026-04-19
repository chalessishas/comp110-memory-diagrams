"""齐尔查克 — generated from ArknightsGameData char_4144_chilc.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4144_chilc
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_chilc() -> UnitState:
    return UnitState(
        name='齐尔查克',
        faction=Faction.ALLY,
        max_hp=1980,
        atk=560,
        defence=317,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=10,
        redeploy_cd=35.0,
    )
