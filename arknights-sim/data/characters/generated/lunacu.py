"""子月 — generated from ArknightsGameData char_4014_lunacu.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4014_lunacu
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_lunacu() -> UnitState:
    return UnitState(
        name='子月',
        faction=Faction.ALLY,
        max_hp=1836,
        atk=1074,
        defence=155,
        res=0.0,
        atk_interval=2.7,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=21,
        redeploy_cd=70.0,
    )
