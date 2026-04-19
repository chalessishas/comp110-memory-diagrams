"""霜叶 — generated from ArknightsGameData char_193_frostl.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_193_frostl
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_frostl() -> UnitState:
    return UnitState(
        name='霜叶',
        faction=Faction.ALLY,
        max_hp=2260,
        atk=660,
        defence=378,
        res=10.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=18,
        redeploy_cd=70.0,
    )
