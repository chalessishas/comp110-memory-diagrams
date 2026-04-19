"""折桠 — generated from ArknightsGameData char_4207_branch.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4207_branch
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_branch() -> UnitState:
    return UnitState(
        name='折桠',
        faction=Faction.ALLY,
        max_hp=4148,
        atk=865,
        defence=590,
        res=10.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=35,
        redeploy_cd=70.0,
    )
