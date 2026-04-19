"""隐现 — generated from ArknightsGameData char_498_inside.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_498_inside
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_inside() -> UnitState:
    return UnitState(
        name='隐现',
        faction=Faction.ALLY,
        max_hp=1440,
        atk=597,
        defence=178,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=15,
        redeploy_cd=80.0,
    )
