"""焰尾 — generated from ArknightsGameData char_420_flamtl.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_420_flamtl
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_flamtl() -> UnitState:
    return UnitState(
        name='焰尾',
        faction=Faction.ALLY,
        max_hp=2138,
        atk=611,
        defence=392,
        res=0.0,
        atk_interval=1.05,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=14,
        redeploy_cd=70.0,
    )
