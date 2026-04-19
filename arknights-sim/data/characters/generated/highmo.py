"""海沫 — generated from ArknightsGameData char_4066_highmo.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4066_highmo
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_highmo() -> UnitState:
    return UnitState(
        name='海沫',
        faction=Faction.ALLY,
        max_hp=2370,
        atk=710,
        defence=454,
        res=0.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=22,
        redeploy_cd=70.0,
    )
