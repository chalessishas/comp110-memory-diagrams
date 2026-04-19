"""天空盒 — generated from ArknightsGameData char_4213_skybx.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4213_skybx
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_skybx() -> UnitState:
    return UnitState(
        name='天空盒',
        faction=Faction.ALLY,
        max_hp=1558,
        atk=984,
        defence=197,
        res=0.0,
        atk_interval=2.1,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=24,
        redeploy_cd=80.0,
    )
