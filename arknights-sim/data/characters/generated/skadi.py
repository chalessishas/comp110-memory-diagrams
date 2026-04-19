"""斯卡蒂 — generated from ArknightsGameData char_263_skadi.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_263_skadi
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_skadi() -> UnitState:
    return UnitState(
        name='斯卡蒂',
        faction=Faction.ALLY,
        max_hp=3866,
        atk=1095,
        defence=303,
        res=0.0,
        atk_interval=1.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=19,
        redeploy_cd=70.0,
    )
