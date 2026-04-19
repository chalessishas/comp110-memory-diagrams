"""伯塔尼 — generated from ArknightsGameData char_4223_botany.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4223_botany
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_botany() -> UnitState:
    return UnitState(
        name='伯塔尼',
        faction=Faction.ALLY,
        max_hp=1320,
        atk=501,
        defence=108,
        res=15.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=17,
        redeploy_cd=80.0,
    )
