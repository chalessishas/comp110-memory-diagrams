"""拉普兰德 — generated from ArknightsGameData char_140_whitew.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_140_whitew
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_whitew() -> UnitState:
    return UnitState(
        name='拉普兰德',
        faction=Faction.ALLY,
        max_hp=2350,
        atk=760,
        defence=365,
        res=15.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=19,
        redeploy_cd=70.0,
    )
