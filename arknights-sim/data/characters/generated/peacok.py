"""断罪者 — generated from ArknightsGameData char_159_peacok.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_159_peacok
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_peacok() -> UnitState:
    return UnitState(
        name='断罪者',
        faction=Faction.ALLY,
        max_hp=3705,
        atk=951,
        defence=188,
        res=0.0,
        atk_interval=1.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=16,
        redeploy_cd=70.0,
    )
