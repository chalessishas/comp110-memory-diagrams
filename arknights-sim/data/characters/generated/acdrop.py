"""酸糖 — generated from ArknightsGameData char_366_acdrop.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_366_acdrop
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_acdrop() -> UnitState:
    return UnitState(
        name='酸糖',
        faction=Faction.ALLY,
        max_hp=1576,
        atk=815,
        defence=209,
        res=0.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=18,
        redeploy_cd=70.0,
    )
