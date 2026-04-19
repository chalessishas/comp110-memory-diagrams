"""涤火杰西卡 — generated from ArknightsGameData char_1034_jesca2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1034_jesca2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_jesca2() -> UnitState:
    return UnitState(
        name='涤火杰西卡',
        faction=Faction.ALLY,
        max_hp=3608,
        atk=582,
        defence=776,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=23,
        redeploy_cd=70.0,
    )
