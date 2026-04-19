"""信仰搅拌机 — generated from ArknightsGameData char_4194_rmixer.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4194_rmixer
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_rmixer() -> UnitState:
    return UnitState(
        name='信仰搅拌机',
        faction=Faction.ALLY,
        max_hp=3677,
        atk=564,
        defence=763,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=25,
        redeploy_cd=80.0,
    )
