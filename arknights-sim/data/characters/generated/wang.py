"""望 — generated from ArknightsGameData char_2027_wang.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_2027_wang
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_wang() -> UnitState:
    return UnitState(
        name='望',
        faction=Faction.ALLY,
        max_hp=1480,
        atk=669,
        defence=174,
        res=0.0,
        atk_interval=0.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=12,
        redeploy_cd=70.0,
    )
