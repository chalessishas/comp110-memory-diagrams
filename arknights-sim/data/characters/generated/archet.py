"""空弦 — generated from ArknightsGameData char_332_archet.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_332_archet
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_archet() -> UnitState:
    return UnitState(
        name='空弦',
        faction=Faction.ALLY,
        max_hp=1705,
        atk=618,
        defence=172,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=14,
        redeploy_cd=70.0,
    )
