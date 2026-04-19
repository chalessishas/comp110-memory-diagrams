"""苍苔 — generated from ArknightsGameData char_4106_bryota.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4106_bryota
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_bryota() -> UnitState:
    return UnitState(
        name='苍苔',
        faction=Faction.ALLY,
        max_hp=1900,
        atk=685,
        defence=456,
        res=0.0,
        atk_interval=1.05,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=18,
        redeploy_cd=80.0,
    )
