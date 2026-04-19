"""温蒂 — generated from ArknightsGameData char_400_weedy.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_400_weedy
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_weedy() -> UnitState:
    return UnitState(
        name='温蒂',
        faction=Faction.ALLY,
        max_hp=2133,
        atk=722,
        defence=439,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=21,
        redeploy_cd=70.0,
    )
