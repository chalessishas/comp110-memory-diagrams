"""维什戴尔 — generated from ArknightsGameData char_1035_wisdel.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1035_wisdel
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_wisdel() -> UnitState:
    return UnitState(
        name='维什戴尔',
        faction=Faction.ALLY,
        max_hp=1888,
        atk=777,
        defence=256,
        res=15.0,
        atk_interval=2.1,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=25,
        redeploy_cd=70.0,
    )
