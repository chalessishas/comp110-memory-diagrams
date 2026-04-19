"""霜华 — generated from ArknightsGameData char_458_rfrost.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_458_rfrost
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_rfrost() -> UnitState:
    return UnitState(
        name='霜华',
        faction=Faction.ALLY,
        max_hp=1559,
        atk=569,
        defence=157,
        res=0.0,
        atk_interval=0.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=11,
        redeploy_cd=70.0,
    )
