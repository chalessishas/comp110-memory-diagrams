"""止颂 — generated from ArknightsGameData char_4011_lessng.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4011_lessng
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_lessng() -> UnitState:
    return UnitState(
        name='止颂',
        faction=Faction.ALLY,
        max_hp=3882,
        atk=1129,
        defence=277,
        res=0.0,
        atk_interval=1.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=21,
        redeploy_cd=80.0,
    )
