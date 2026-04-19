"""赫拉格 — generated from ArknightsGameData char_188_helage.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_188_helage
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_helage() -> UnitState:
    return UnitState(
        name='赫拉格',
        faction=Faction.ALLY,
        max_hp=4225,
        atk=832,
        defence=334,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=26,
        redeploy_cd=70.0,
    )
