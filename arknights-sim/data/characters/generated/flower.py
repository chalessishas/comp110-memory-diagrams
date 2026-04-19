"""调香师 — generated from ArknightsGameData char_181_flower.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_181_flower
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_flower() -> UnitState:
    return UnitState(
        name='调香师',
        faction=Faction.ALLY,
        max_hp=1710,
        atk=345,
        defence=145,
        res=0.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=16,
        redeploy_cd=70.0,
    )
