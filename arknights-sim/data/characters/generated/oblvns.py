"""丰川祥子 — generated from ArknightsGameData char_4182_oblvns.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4182_oblvns
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_oblvns() -> UnitState:
    return UnitState(
        name='丰川祥子',
        faction=Faction.ALLY,
        max_hp=2356,
        atk=785,
        defence=425,
        res=10.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=20,
        redeploy_cd=70.0,
    )
