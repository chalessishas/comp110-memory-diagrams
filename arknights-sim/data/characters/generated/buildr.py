"""青枳 — generated from ArknightsGameData char_488_buildr.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_488_buildr
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_buildr() -> UnitState:
    return UnitState(
        name='青枳',
        faction=Faction.ALLY,
        max_hp=2215,
        atk=475,
        defence=410,
        res=0.0,
        atk_interval=1.05,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=13,
        redeploy_cd=70.0,
    )
