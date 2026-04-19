"""红 — generated from ArknightsGameData char_144_red.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_144_red
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_red() -> UnitState:
    return UnitState(
        name='红',
        faction=Faction.ALLY,
        max_hp=1505,
        atk=605,
        defence=302,
        res=0.0,
        atk_interval=0.93,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=9,
        redeploy_cd=18.0,
    )
