"""归溟幽灵鲨 — generated from ArknightsGameData char_1023_ghost2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1023_ghost2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_ghost2() -> UnitState:
    return UnitState(
        name='归溟幽灵鲨',
        faction=Faction.ALLY,
        max_hp=2803,
        atk=817,
        defence=322,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=16,
        redeploy_cd=70.0,
    )
