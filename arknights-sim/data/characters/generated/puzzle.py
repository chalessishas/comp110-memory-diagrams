"""谜图 — generated from ArknightsGameData char_4017_puzzle.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4017_puzzle
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_puzzle() -> UnitState:
    return UnitState(
        name='谜图',
        faction=Faction.ALLY,
        max_hp=1860,
        atk=606,
        defence=264,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=12,
        redeploy_cd=35.0,
    )
