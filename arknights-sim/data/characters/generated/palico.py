"""泰拉大陆调查团 — generated from ArknightsGameData char_4077_palico.
Source: E0 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4077_palico
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_palico() -> UnitState:
    return UnitState(
        name='泰拉大陆调查团',
        faction=Faction.ALLY,
        max_hp=618,
        atk=306,
        defence=51,
        res=0.0,
        atk_interval=2.1,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=3,
        redeploy_cd=200.0,
    )
