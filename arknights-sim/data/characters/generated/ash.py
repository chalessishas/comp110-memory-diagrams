"""灰烬 — generated from ArknightsGameData char_456_ash.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_456_ash
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_ash() -> UnitState:
    return UnitState(
        name='灰烬',
        faction=Faction.ALLY,
        max_hp=1689,
        atk=624,
        defence=169,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=14,
        redeploy_cd=70.0,
    )
