"""梓兰 — generated from ArknightsGameData char_278_orchid.
Source: E1 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_278_orchid
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_orchid() -> UnitState:
    return UnitState(
        name='梓兰',
        faction=Faction.ALLY,
        max_hp=935,
        atk=418,
        defence=83,
        res=15.0,
        atk_interval=1.9,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=12,
        redeploy_cd=70.0,
    )
