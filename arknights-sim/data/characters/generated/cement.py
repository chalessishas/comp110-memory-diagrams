"""洋灰 — generated from ArknightsGameData char_464_cement.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_464_cement
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_cement() -> UnitState:
    return UnitState(
        name='洋灰',
        faction=Faction.ALLY,
        max_hp=3642,
        atk=1042,
        defence=688,
        res=0.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=32,
        redeploy_cd=70.0,
    )
