"""余 — generated from ArknightsGameData char_2026_yu.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_2026_yu
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_yu() -> UnitState:
    return UnitState(
        name='余',
        faction=Faction.ALLY,
        max_hp=3633,
        atk=715,
        defence=607,
        res=10.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=26,
        redeploy_cd=70.0,
    )
