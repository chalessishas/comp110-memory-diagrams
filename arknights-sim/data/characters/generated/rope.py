"""暗索 — generated from ArknightsGameData char_236_rope.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_236_rope
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_rope() -> UnitState:
    return UnitState(
        name='暗索',
        faction=Faction.ALLY,
        max_hp=1720,
        atk=728,
        defence=385,
        res=0.0,
        atk_interval=1.8,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=12,
        redeploy_cd=70.0,
    )
