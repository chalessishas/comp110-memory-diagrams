"""火龙S黑角 — generated from ArknightsGameData char_1030_noirc2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1030_noirc2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_noirc2() -> UnitState:
    return UnitState(
        name='火龙S黑角',
        faction=Faction.ALLY,
        max_hp=3518,
        atk=766,
        defence=391,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=25,
        redeploy_cd=70.0,
    )
