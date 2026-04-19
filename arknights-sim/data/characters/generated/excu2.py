"""圣约送葬人 — generated from ArknightsGameData char_1032_excu2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1032_excu2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_excu2() -> UnitState:
    return UnitState(
        name='圣约送葬人',
        faction=Faction.ALLY,
        max_hp=2491,
        atk=777,
        defence=491,
        res=0.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=23,
        redeploy_cd=70.0,
    )
