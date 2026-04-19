"""阿 — generated from ArknightsGameData char_225_haak.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_225_haak
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_haak() -> UnitState:
    return UnitState(
        name='阿',
        faction=Faction.ALLY,
        max_hp=2334,
        atk=753,
        defence=152,
        res=10.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=13,
        redeploy_cd=70.0,
    )
