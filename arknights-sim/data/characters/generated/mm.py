"""梅 — generated from ArknightsGameData char_133_mm.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_133_mm
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_mm() -> UnitState:
    return UnitState(
        name='梅',
        faction=Faction.ALLY,
        max_hp=1632,
        atk=543,
        defence=105,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=12,
        redeploy_cd=70.0,
    )
