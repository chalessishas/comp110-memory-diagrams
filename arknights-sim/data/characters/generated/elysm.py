"""极境 — generated from ArknightsGameData char_401_elysm.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_401_elysm
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_elysm() -> UnitState:
    return UnitState(
        name='极境',
        faction=Faction.ALLY,
        max_hp=1669,
        atk=533,
        defence=395,
        res=0.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=11,
        redeploy_cd=70.0,
    )
