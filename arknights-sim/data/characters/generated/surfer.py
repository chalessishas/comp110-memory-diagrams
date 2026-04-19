"""寻澜 — generated from ArknightsGameData char_4052_surfer.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4052_surfer
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_surfer() -> UnitState:
    return UnitState(
        name='寻澜',
        faction=Faction.ALLY,
        max_hp=1950,
        atk=600,
        defence=281,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=10,
        redeploy_cd=35.0,
    )
