"""讯使 — generated from ArknightsGameData char_198_blackd.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_198_blackd
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_blackd() -> UnitState:
    return UnitState(
        name='讯使',
        faction=Faction.ALLY,
        max_hp=1985,
        atk=435,
        defence=382,
        res=0.0,
        atk_interval=1.05,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=12,
        redeploy_cd=70.0,
    )
